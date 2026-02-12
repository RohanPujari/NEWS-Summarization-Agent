from fastapi import FastAPI
from storage.repository import ArticleRepository

app = FastAPI()

repo = ArticleRepository()


@app.get("/")
def home():
    return {"message": "News Summarization API is running"}


@app.get("/articles")
def get_articles(limit: int = 10, offset: int = 0):
    rows = repo.fetch_latest(limit=limit, offset=offset)

    articles = []
    for row in rows:
        articles.append({
            "title": row[0],
            "summary": row[1],
            "published_at": row[2]
        })

    return {"articles": articles}