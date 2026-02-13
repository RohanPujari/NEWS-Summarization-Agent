from fastapi import FastAPI
from storage.repository import ArticleRepository
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allow all origins for now
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
            "image_url": row[2],
            "published_at": row[3]
        })

    return {"articles": articles}