from agent.news_agent import NewsAgent

FEED_URL = "https://feeds.bbci.co.uk/news/rss.xml"  # keep BBC for now

agent = NewsAgent(FEED_URL)
results = agent.run(limit=5)

print("\n===== PIPELINE RESULT =====")
print("Total summaries generated:", len(results))

for r in results:
    print("\nTITLE:", r["title"])
    print("SUMMARY:", r["summary"][:200], "...")
