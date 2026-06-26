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
            return JSONResponse({"error": "Missing API keys"}, status_code=500)
        
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
        
        # Summarize with Claude via HTTP
        results = []
        
        for article in articles:
            title = article.get("title", "")
            description = article.get("description", "")
            
            if not description or len(description) < 50:
                continue
            
            try:
                # Direct HTTP request to Anthropic API
                claude_response = requests.post(
                    "https://api.anthropic.com/v1/messages",
                    headers={
                        "x-api-key": anthropic_key,
                        "anthropic-version": "2023-06-01",
                        "content-type": "application/json"
                    },
                    json={
                        "model": "claude-opus-4-6",
                        "max_tokens": 256,
                        "messages": [{
                            "role": "user",
                            "content": f"Summarize in 80-120 words:\n\nTitle: {title}\n\nContent: {description}"
                        }]
                    },
                    timeout=30
                )
                
                if claude_response.status_code == 200:
                    summary_data = claude_response.json()
                    summary = summary_data.get("content", [{}])[0].get("text", "")
                    
                    if summary:
                        results.append({
                            "title": title,
                            "summary": summary,
                            "url": article.get("url"),
                            "published_at": article.get("publishedAt"),
                            "source": article.get("source", {}).get("name", "")
                        })
            
            except Exception as e:
                print(f"Error: {e}")
                continue
        
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