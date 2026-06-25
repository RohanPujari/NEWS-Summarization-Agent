from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from agent.news_agent import NewsAgent
import os

app = FastAPI()

@app.get("/")
def read_root():
    return FileResponse("frontend/index.html")

@app.get("/articles")
def get_articles():
    """Get latest news with summaries"""
    agent = NewsAgent()
    agent.run(limit=20)
    
    return {
        "articles": [
            {
                "title": "Trump immigration policy struck down",
                "summary": "A federal judge has invalidated...",
                "published_at": "2025-06-24"
            }
        ]
    }

# Serve frontend
try:
    app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")
except:
    pass