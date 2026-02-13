from ingestion.rss_fetcher import RSSFetcher
from processing.cleaner import ArticleCleaner
from processing.summarizer import PegasusSummarizer
from storage.db import init_db
from storage.repository import ArticleRepository


init_db()

class NewsAgent:
    def __init__(self, feed_url: str):
        self.fetcher = RSSFetcher(feed_url)
        self.cleaner = ArticleCleaner()
        self.summarizer = PegasusSummarizer()
        self.repo = ArticleRepository()


    def run(self, limit: int = 5):
        articles = self.fetcher.fetch()
        results = []

        print(f"[AGENT] Fetched {len(articles)} articles")

        for article in articles[:limit]:
            title = article.get("title", "")
            url = article.get("url", "")

            print(f"\n[AGENT] Processing: {title}")
            # SQL Injection
            if self.repo.exists(url):
                print("[AGENT] Skipping (already stored)")
                continue

            text, image_url = self.cleaner.extract(url)
            print(f"[AGENT] Extracted words: {len(text.split())}")

            if not text:
                print("[AGENT] Skipping: empty text")
                continue

            summary = self.summarizer.summarize(text)

            if not summary:
                print("[AGENT] Skipping: summary empty")
                continue

            self.repo.save(title=title, url=url, summary=summary, image_url=image_url, published_at=article.get("published"))
            print("[AGENT] Saved article")
            
            results.append({
                "title": title,
                "url": url,
                "summary": summary
            })

        return results
