import requests
import os

class NewsAPIFetcher:
    def __init__(self):
        self.api_key = os.getenv("NEWS_API_KEY")
        self.base_url = "https://newsapi.org/v2"
    
    def fetch_latest(self, limit=100):
        """Fetch latest news from NewsAPI"""
        
        if not self.api_key:
            print("[NewsAPI] API key not found")
            return []
        
        url = f"{self.base_url}/top-headlines"
        params = {
            "country": "us",
            "sortBy": "publishedAt",
            "pageSize": limit,
            "apiKey": self.api_key
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            articles = []
            for article in data.get("articles", []):
                articles.append({
                    "title": article["title"],
                    "content": article.get("description", ""),
                    "url": article["url"],
                    "published_at": article["publishedAt"],
                    "source": article["source"]["name"]
                })
            
            print(f"[NewsAPI] Fetched {len(articles)} articles")
            return articles
        
        except Exception as e:
            print(f"[NewsAPI Error] {e}")
            return []