from processing.cleaner import ArticleCleaner
from processing.summarizer import BartSummarizer

url = "https://www.bbc.com/news/articles/cy8p2re7gj5o"

cleaner = ArticleCleaner()
summarizer = BartSummarizer()

text = cleaner.extract(url)
summary = summarizer.summarize(text)

print("SUMMARY:\n")
print(summary)
print("\nWord count:", len(summary.split()))
