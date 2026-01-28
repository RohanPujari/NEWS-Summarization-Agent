from ingestion.rss_fetcher import RSSFetcher

fetcher = RSSFetcher("https://feeds.bbci.co.uk/news/rss.xml")
articles = fetcher.fetch()

print(f"Fetched {len(articles)} articles")
if articles:
    print(articles[0])
