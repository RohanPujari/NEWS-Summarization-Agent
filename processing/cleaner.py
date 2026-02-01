from newspaper import Article

class ArticleCleaner:
    def extract(self, url: str) -> str:
        try:
            article = Article(url)
            article.download()
            article.parse()
            return article.text.strip()
        except Exception as e:
            print(f"[ERROR] Extraction failed: {e}")
            return ""
