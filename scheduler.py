from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
import requests
import anthropic
import os
from datetime import datetime
from dotenv import load_dotenv
from models import SessionLocal, Article

load_dotenv()

def scheduled_fetch_news():
    """Fetch and summarize news every 2 hours"""
    try:
        print(f"[SCHEDULER] Running at {datetime.now()}")
        
        api_key = os.getenv("NEWS_API_KEY")
        anthropic_key = os.getenv("ANTHROPIC_API_KEY")
        
        if not api_key or not anthropic_key:
            print("[SCHEDULER] Missing API keys")
            return
        
        url = "https://newsapi.org/v2/top-headlines"
        params = {
            "country": "us",
            "pageSize": 50,
            "apiKey": api_key
        }
        
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        articles = data.get("articles", [])
        
        print(f"[SCHEDULER] Fetched {len(articles)} articles")
        
        db = SessionLocal()
        client = anthropic.Anthropic(api_key=anthropic_key)
        count = 0
        
        for article_data in articles:
            existing = db.query(Article).filter(
                Article.url == article_data.get("url")
            ).first()
            
            if existing:
                continue
            
            title = article_data.get("title", "")
            description = article_data.get("description", "")
            
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
                
                article = Article(
                    title=title,
                    summary=summary,
                    url=article_data.get("url", ""),
                    source=article_data.get("source", {}).get("name", ""),
                    published_at=datetime.fromisoformat(
                        article_data.get("publishedAt", "").replace("Z", "+00:00")
                    ) if article_data.get("publishedAt") else datetime.utcnow()
                )
                
                db.add(article)
                count += 1
            
            except Exception as e:
                print(f"[SCHEDULER] Error: {e}")
                continue
        
        db.commit()
        db.close()
        
        print(f"[SCHEDULER] Saved {count} new articles")
    
    except Exception as e:
        print(f"[SCHEDULER] Error: {e}")

def start_scheduler():
    """Start background scheduler"""
    scheduler = BackgroundScheduler()
    
    scheduler.add_job(
        scheduled_fetch_news,
        IntervalTrigger(hours=2),
        id='fetch_news',
        name='Fetch and summarize news',
        replace_existing=True
    )
    
    scheduler.start()
    print("[SCHEDULER] Started - will fetch news every 2 hours")
    
    return scheduler