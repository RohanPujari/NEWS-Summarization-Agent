import requests
import anthropic
import os
from dotenv import load_dotenv

load_dotenv()

def get_summaries(limit=5):
    """Fetch and summarize news from NewsAPI"""
    
    api_key = os.getenv("NEWS_API_KEY")
    
    if not api_key:
        print("ERROR: NEWS_API_KEY not in .env")
        return 0
    
    url = "https://newsapi.org/v2/top-headlines"
    params = {
        "country": "us",
        "pageSize": limit,
        "apiKey": api_key
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        articles = data.get("articles", [])
        print(f"Fetched {len(articles)} articles")
        
        client = anthropic.Anthropic()
        count = 0
        
        for article in articles:
            title = article.get("title", "No title")
            description = article.get("description", "")
            
            if len(description) < 50:
                continue
            
            print(f"\nProcessing: {title}")
            
            message = client.messages.create(
                model="claude-opus-4-6",
                max_tokens=256,
                messages=[{
                    "role": "user",
                    "content": f"Summarize in 80-120 words:\n\n{title}\n{description}"
                }]
            )
            
            summary = message.content[0].text
            print(f"Summary: {summary[:100]}...")
            count += 1
        
        print(f"\n✅ Generated {count} summaries")
        return count
    
    except Exception as e:
        print(f"Error: {e}")
        return 0

if __name__ == "__main__":
    get_summaries(limit=5)