from fastapi import FastAPI, Depends, HTTPException, WebSocket
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from models import get_db, Article, UserRating
from scheduler import start_scheduler
from categorization import categorize_article
import requests
import os
from dotenv import load_dotenv
from datetime import datetime
from typing import List
from groq import Groq

load_dotenv()

import re

def clean_url(url: str) -> str:
    """Remove Markdown link formatting from URLs."""
    if not url:
        return ""

    if url.startswith("[") and "](" in url and url.endswith(")"):
        return url.split("](", 1)[1][:-1]

    return url

app = FastAPI(title="News Summarizer API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

scheduler = start_scheduler()

@app.on_event("startup")
async def startup():
    print("[APP] Started with scheduler")

@app.on_event("shutdown")
async def shutdown():
    scheduler.shutdown()

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
    
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
    
    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                pass

manager = ConnectionManager()



def summarize_with_groq(title: str, content: str) -> str:
    """Generate a concise news summary using Groq."""
    try:
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            print("[GROQ] Missing GROQ_API_KEY")
            return "Summary unavailable"

        client = Groq(api_key=api_key)

        print(f"[GROQ] Summarizing: {title[:50]}...")

        message = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            reasoning_effort="low",
            max_tokens=500,
            messages=[
                {
                    "role": "user",
                    "content": (
                        "Write a concise, factual summary of the article "
                        "in approximately 60 words. "
                        "Return ONLY the final summary. "
                        "Do not explain your reasoning or include a title.\n\n"
                        f"Title: {title}\n\n"
                        f"Content: {content}"
                    ),
                }
            ],
        )

        summary = message.choices[0].message.content.strip()

        if not summary:
            print("[GROQ] Empty response")
            return "Summary unavailable"

        print(f"[GROQ] Generated {len(summary.split())} words")
        return summary

    except Exception as e:
        print(f"[GROQ ERROR] {str(e)}")
        return "Summary unavailable"



@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/")
def root():
    try:
        return FileResponse("frontend/index.html")
    except:
        return {"message": "News API"}

@app.get("/api/articles")
def get_articles(skip: int = 0, limit: int = 20, search: str = None, category: str = None, db: Session = Depends(get_db)):
    try:
        query = db.query(Article).order_by(Article.published_at.desc())
        
        if search:
            query = query.filter(
                (Article.title.ilike(f"%{search}%")) |
                (Article.summary.ilike(f"%{search}%"))
            )
        
        # ADD THIS: Filter by category
        if category and category != "all":
            query = query.filter(Article.category == category)
        
        total = query.count()
        articles = query.offset(skip).limit(limit).all()
        
        return {
            "status": "success",
            "total": total,
            "articles": [
                {
                    "id": a.id,
                    "title": a.title,
                    "summary": a.summary,
                    "url": a.url,
                    "source": a.source,
                    "category": a.category,  # ADD THIS
                    "published_at": a.published_at.isoformat() if a.published_at else None,
                    "image": a.image_url,
                }
                for a in articles
            ]
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.post("/api/rate")
def rate_article(article_id: int, rating: int, comment: str = None, db: Session = Depends(get_db)):
    try:
        if rating < 1 or rating > 5:
            raise HTTPException(status_code=400, detail="Rating 1-5")
        
        article = db.query(Article).filter(Article.id == article_id).first()
        if not article:
            raise HTTPException(status_code=404, detail="Article not found")
        
        user_rating = UserRating(article_id=article_id, rating=rating, comment=comment)
        db.add(user_rating)
        db.commit()
        
        return {"status": "success"}
    except Exception as e:
        db.rollback()
        return {"status": "error", "message": str(e)}


@app.get("/api/fetch-now")
def fetch_now(db: Session = Depends(get_db)):
    try:
        api_key = os.getenv("NEWS_API_KEY")
        if not api_key:
            return {"status": "error", "message": "No API key"}
        
        url = "https://newsapi.org/v2/top-headlines"
        params = {"country": "us", "pageSize": 50, "apiKey": api_key}
        
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        articles = data.get("articles", [])
        
        count = 0
        for article_data in articles:
            existing = db.query(Article).filter(Article.url == article_data.get("url")).first()
            if existing:
                continue
            
            title = article_data.get("title", "")
            description = article_data.get("description", "")
            # image = article_data.get("urlToImage", "")

            # print(f"[DEBUG] Title: {title[:50]}")
            # print(f"[DEBUG] Image: {image}")  # ADD THIS
            
            if not description or len(description) < 50:
                continue
            
            summary = summarize_with_groq(title, description)

            category = categorize_article(title, summary)

            article = Article(
                title=title,
                summary=summary,
                url=clean_url(article_data.get("url", "")),
                category=category,
                source=article_data.get("source", {}).get("name", ""),
                image_url=clean_url(article_data.get("urlToImage", "")),
                published_at=datetime.fromisoformat(article_data.get("publishedAt", "").replace("Z", "+00:00")) if article_data.get("publishedAt") else datetime.utcnow()
            )
            db.add(article)
            count += 1
        db.commit()
        return {"status": "success", "message": f"Fetched {count} articles"}
    except Exception as e:
        db.rollback()
        return {"status": "error", "message": str(e)}

@app.get("/api/stats")
def stats(db: Session = Depends(get_db)):
    try:
        total = db.query(Article).count()
        ratings = db.query(UserRating).count()
        return {"status": "success", "total_articles": total, "total_ratings": ratings}
    except:
        return {"status": "error"}

@app.websocket("/ws/articles")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
    except:
        manager.disconnect(websocket)