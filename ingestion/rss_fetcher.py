import feedparser
from typing import List, Dict

class RSSFetcher:
    """
    Fetches latest news articles from an RSS feed.
    """

    def __init__(self, feed_url: str):
        self.feed_url = feed_url

    def fetch(self) -> List[Dict]:
        feed = feedparser.parse(
            self.feed_url,
            request_headers={
                "User-Agent": "Mozilla/5.0 (NewsSummarizationAgent)"
            }
        )

        articles = []

        for entry in feed.entries:
            articles.append({
                "title": entry.get("title", ""),
                "url": entry.get("link", ""),
                "published": entry.get("published", None)
            })

        return articles
