from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse
from agent.news_agent import NewsAgent
import os

app = FastAPI()

@app.get("/")
async def root():
    """Serve frontend"""
    try:
        return FileResponse("frontend/index.html")
    except:
        return {"message": "News Summarizer API - visit /articles for news"}

@app.get("/articles")
async def get_articles():
    """Get latest news with summaries"""
    try:
        agent = NewsAgent()
        count = agent.run(limit=10)
        
        return JSONResponse({
            "status": "success",
            "total": count,
            "message": f"Generated {count} summaries"
        })
    except Exception as e:
        return JSONResponse({
            "status": "error",
            "message": str(e)
        })

@app.get("/health")
async def health():
    """Health check"""
    return {"status": "ok"}