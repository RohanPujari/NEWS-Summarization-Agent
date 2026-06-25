from agent.news_agent import NewsAgent

agent = NewsAgent()
results = agent.run(limit=5)
print(f"Done! Generated {results} summaries")

if __name__ == "__main__":
    agent = NewsAgent()
    agent.run(limit=10)