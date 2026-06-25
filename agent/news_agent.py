import requests
import os
from dotenv import load_dotenv

load_dotenv()

class NewsAgent:
    def __init__(self):
        self.api_key = os.getenv("ANTHROPIC_API_KEY")
        self.news_api_key = os.getenv("NEWS_API_KEY")
    
    def run(self, limit=10):
        """Fetch and summarize news"""
        
        if not self.news_api_key:
            print("[ERROR] NEWS_API_KEY not found")
            return 0
        
        if not self.api_key:
            print("[ERROR] ANTHROPIC_API_KEY not found")
            return 0
        
        url = "https://newsapi.org/v2/top-headlines"
        params = {
            "country": "us",
            "pageSize": limit,
            "apiKey": self.news_api_key
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            articles = data.get("articles", [])
            print(f"[AGENT] Fetched {len(articles)} articles from NewsAPI")
            
            if not articles:
                print("[AGENT] No articles returned from NewsAPI")
                return 0
            
            count = 0
            for i, article in enumerate(articles):
                title = article.get("title", "")
                content = article.get("description", "")
                
                print(f"[AGENT] Article {i+1}: {title}")
                print(f"[AGENT] Content length: {len(content) if content else 0}")
                
                if not content or len(content) < 50:
                    print(f"[AGENT] Skipping - content too short")
                    continue
                
                print(f"[AGENT] Summarizing...")
                summary = self._summarize(title, content)
                
                if summary:
                    print(f"[AGENT] Success!")
                    count += 1
                else:
                    print(f"[AGENT] Summarization failed")
            
            print(f"[AGENT] Total generated: {count} summaries")
            return count
        
        except Exception as e:
            print(f"[ERROR] {str(e)}")
            return 0
    
    def _summarize(self, title, content):
        """Summarize using Claude"""
        
        try:
            import anthropic
            
            client = anthropic.Anthropic(api_key=self.api_key)
            
            message = client.messages.create(
                model="claude-opus-4-6",
                max_tokens=256,
                messages=[{
                    "role": "user",
                    "content": f"Summarize in 80-120 words:\n\nTitle: {title}\n\nContent: {content}"
                }]
            )
            
            return message.content[0].text
        
        except Exception as e:
            print(f"[Claude Error] {str(e)}")
            return None