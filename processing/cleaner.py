from newspaper import Article


class ArticleCleaner:
    """
    Downloads and extracts clean text content from a news article URL.
    """

    def extract(self, url: str) -> str:
        try:
            article = Article(url)
            article.download()
            article.parse()

            text = article.text.strip()
            return text

        except Exception as e:
            print(f"[ERROR] Failed to extract article from {url}: {e}")
            return ""
