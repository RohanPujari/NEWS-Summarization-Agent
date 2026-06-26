# from fastapi import FastAPI
# from fastapi.responses import FileResponse, JSONResponse
# import requests
# import anthropic
# import os
# from dotenv import load_dotenv

# load_dotenv()

# app = FastAPI()

# @app.get("/")
# async def root():
#     try:
#         return FileResponse("frontend/index.html")
#     except:
#         return {"message": "News Summarizer API"}

# @app.get("/articles")
# async def get_articles():
#     try:
#         api_key = os.getenv("NEWS_API_KEY")
#         anthropic_key = os.getenv("ANTHROPIC_API_KEY")
        
#         # Fetch news
#         url = "https://newsapi.org/v2/top-headlines"
#         params = {
#             "country": "us",
#             "pageSize": 10,
#             "apiKey": api_key
#         }
        
#         response = requests.get(url, params=params, timeout=10)
#         data = response.json()
#         articles = data.get("articles", [])
        
#         if not articles:
#             return {"status": "success", "total": 0, "articles": []}
        
#         # Summarize
#         client = anthropic.Anthropic(api_key=anthropic_key)
#         results = []
        
#         for article in articles:
#             title = article.get("title", "")
#             description = article.get("description", "")
            
#             if not description or len(description) < 50:
#                 continue
            
#             message = client.messages.create(
#                 model="claude-opus-4-6",
#                 max_tokens=256,
#                 messages=[{
#                     "role": "user",
#                     "content": f"Summarize in 80-120 words:\n\nTitle: {title}\n\nContent: {description}"
#                 }]
#             )
            
#             summary = message.content[0].text
            
#             results.append({
#                 "title": title,
#                 "summary": summary,
#                 "url": article.get("url"),
#                 "published_at": article.get("publishedAt"),
#                 "source": article.get("source", {}).get("name", "")
#             })
        
#         return {
#             "status": "success",
#             "total": len(results),
#             "articles": results
#         }
    
#     except Exception as e:
#         return JSONResponse({"error": str(e)}, status_code=500)

# @app.get("/health")
# async def health():
#     return {"status": "ok"}

from fastapi import FastAPI, Depends, HTTPException, WebSocket
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from models import get_db, Article, UserRating
from scheduler import start_scheduler
import requests
import anthropic
import os
from dotenv import load_dotenv
from datetime import datetime
from typing import List

load_dotenv()

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

def summarize_with_claude(title: str, content: str) -> str:
    try:
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            return "No API key configured"
        
        print(f"[Claude] Summarizing: {title[:50]}...")
        
        response = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json"
            },
            json={
                "model": "claude-opus-4-6",
                "max_tokens": 200,  # Reduced from 500
                "messages": [{
                    "role": "user",
                    "content": f"Create a brief 60-65 word summary:\n\nTitle: {title}\n\nContent: {content}"
                }]
            },
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            summary = data.get("content", [{}])[0].get("text", "")
            print(f"[Claude] Generated {len(summary.split())} word summary")
            return summary
        else:
            print(f"[Claude Error] Status {response.status_code}")
            return f"Error: {response.status_code}"
    
    except Exception as e:
        print(f"[Claude ERROR] {str(e)}")
        return f"Error: {str(e)}"

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
def get_articles(skip: int = 0, limit: int = 20, search: str = None, db: Session = Depends(get_db)):
    try:
        query = db.query(Article).order_by(Article.published_at.desc())
        
        if search:
            query = query.filter(
                (Article.title.ilike(f"%{search}%")) |
                (Article.summary.ilike(f"%{search}%"))
            )
        
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
                    "published_at": a.published_at.isoformat() if a.published_at else None,
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
            
            if not description or len(description) < 50:
                continue
            
            summary = summarize_with_claude(title, description)
            
            article = Article(
                title=title,
                summary=summary,
                url=article_data.get("url", ""),
                source=article_data.get("source", {}).get("name", ""),
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