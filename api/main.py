from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse
import requests
import anthropic
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

@app.get("/")
async def root():
    try:
        return FileResponse("frontend/index.html")
    except:
        return {"message": "News Summarizer API"}

@app.get("/articles")
async def get_articles():
    try:
        api_key = os.getenv("NEWS_API_KEY")
        anthropic_key = os.getenv("ANTHROPIC_API_KEY")
        
        # Fetch news
        url = "https://newsapi.org/v2/top-headlines"
        params = {
            "country": "us",
            "pageSize": 10,
            "apiKey": api_key
        }
        
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        articles = data.get("articles", [])
        
        if not articles:
            return {"status": "success", "total": 0, "articles": []}
        
        # Summarize
        client = anthropic.Anthropic(api_key=anthropic_key)
        results = []
        
        for article in articles:
            title = article.get("title", "")
            description = article.get("description", "")
            
            if not description or len(description) < 50:
                continue
            
            message = client.messages.create(
                model="claude-opus-4-6",
                max_tokens=256,
                messages=[{
                    "role": "user",
                    "content": f"Summarize in 80-120 words:\n\nTitle: {title}\n\nContent: {description}"
                }]
            )
            
            summary = message.content[0].text
            
            results.append({
                "title": title,
                "summary": summary,
                "url": article.get("url"),
                "published_at": article.get("publishedAt"),
                "source": article.get("source", {}).get("name", "")
            })
        
        return {
            "status": "success",
            "total": len(results),
            "articles": results
        }
    
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

@app.get("/health")
async def health():
    return {"status": "ok"}