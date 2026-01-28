from processing.cleaner import ArticleCleaner

url = "https://www.bbc.com/news/articles/cy8p2re7gj5o"

cleaner = ArticleCleaner()
text = cleaner.extract(url)

print(f"Extracted {len(text.split())} words")
print(text[:500])
