import requests
import anthropic
import os
from dotenv import load_dotenv

load_dotenv()

class NewsAgent:
    def __init__(self):
        self.client = anthropic.Anthropic()
        self.api_key = os.getenv("NEWS_API_KEY")
    
    def run(self, limit=10):
        """Fetch and summarize news from NewsAPI"""
        
        if not self.api_key:
            print("[ERROR] NEWS_API_KEY not in .env")
            return 0
        
        url = "https://newsapi.org/v2/top-headlines"
        params = {
            "country": "us",
            "pageSize": limit,
            "apiKey": self.api_key
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            articles = data.get("articles", [])
            print(f"[AGENT] Fetched {len(articles)} articles")
            
            count = 0
            for article in articles:
                title = article.get("title", "")
                content = article.get("description", "")
                
                if not content or len(content) < 50:
                    continue
                
                print(f"\n[AGENT] Processing: {title}")
                
                summary = self._summarize(title, content)
                
                if summary:
                    print(f"[AGENT] Summary: {summary[:80]}...")
                    count += 1
            
            print(f"\n===== TOTAL: {count} summaries =====")
            return count
        
        except Exception as e:
            print(f"[ERROR] {e}")
            return 0
    
    def _summarize(self, title, content):
        """Summarize using Claude"""
        
        try:
            message = self.client.messages.create(
                model="claude-opus-4-6",
                max_tokens=256,
                messages=[{
                    "role": "user",
                    "content": f"Summarize in 80-120 words:\n\nTitle: {title}\n\nContent: {content}"
                }]
            )
            
            return message.content[0].text
        
        except Exception as e:
            print(f"[Claude Error] {e}")
            return None