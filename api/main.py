from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse
import requests
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

@app.get("/")
async def root():
    """Serve frontend"""
    try:
        return FileResponse("frontend/index.html")
    except:
        return {"message": "News Summarizer API"}

@app.get("/articles")
async def get_articles():
    """Get latest news with summaries"""
    try:
        api_key = os.getenv("NEWS_API_KEY")
        anthropic_key = os.getenv("ANTHROPIC_API_KEY")
        
        if not api_key or not anthropic_key:
            return JSONResponse({
                "status": "error",
                "message": "Missing API keys"
            }, status_code=500)
        
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
            return JSONResponse({
                "status": "success",
                "total": 0,
                "articles": [],
                "message": "No articles found"
            })
        
        # Summarize with Claude
        import anthropic
        
        client = anthropic.Anthropic(api_key=anthropic_key)
        results = []
        
        for article in articles:
            title = article.get("title", "")
            description = article.get("description", "")
            
            if not description or len(description) < 50:
                continue
            
            try:
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
            
            except Exception as e:
                print(f"Error summarizing: {e}")
                continue
        
        return JSONResponse({
            "status": "success",
            "total": len(results),
            "articles": results
        })
    
    except Exception as e:
        return JSONResponse({
            "status": "error",
            "message": str(e)
        }, status_code=500)

@app.get("/health")
async def health():
    """Health check"""
    return {"status": "ok"}