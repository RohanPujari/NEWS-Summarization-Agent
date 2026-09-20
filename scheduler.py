from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from categorization import categorize_article
import requests
import os
from datetime import datetime
from dotenv import load_dotenv
from models import SessionLocal, Article
from groq import Groq

def clean_url(url: str) -> str:
    if not url:
        return ""

    if url.startswith("[") and "](" in url and url.endswith(")"):
        return url.split("](", 1)[1][:-1]

    return url

load_dotenv()


def summarize_with_groq(title: str, content: str) -> str:
    """Generate a concise news summary using Groq."""
    try:
        api_key = os.getenv("GROQ_API_KEY")

        if not api_key:
            print("[GROQ] Missing GROQ_API_KEY")
            return "Summary unavailable"

        client = Groq(api_key=api_key)

        print(f"[GROQ] Summarizing: {title[:50]}...")

        message = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        max_tokens=500,
        reasoning_effort="low",
        messages=[
            {
                "role": "user",
                "content": (
                    "Write a concise, factual summary of the article in approximately 60 words."
                    "Return ONLY the final summary. "
                    "Do not explain your reasoning.\n\n"
                    f"Title: {title}\n\n"
                    f"Content: {content}"
                ),
            }
        ],
    )

        summary = message.choices[0].message.content.strip()

        print(f"[GROQ] Generated {len(summary.split())} words")

        return summary

    except Exception as e:
        print(f"[GROQ ERROR] {str(e)}")
        return "Summary unavailable"


def scheduled_fetch_news():
    """Fetch and summarize news every 2 hours."""

    db = None

    try:
        print(f"[SCHEDULER] Running at {datetime.now()}")

        news_api_key = os.getenv("NEWS_API_KEY")
        groq_api_key = os.getenv("GROQ_API_KEY")

        if not news_api_key:
            print("[SCHEDULER] Missing NEWS_API_KEY")
            return

        if not groq_api_key:
            print("[SCHEDULER] Missing GROQ_API_KEY")
            return

        # Fetch news
        url = "https://newsapi.org/v2/top-headlines"

        params = {
            "country": "us",
            "pageSize": 50,
            "apiKey": news_api_key,
        }

        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()

        data = response.json()
        articles = data.get("articles", [])

        print(f"[SCHEDULER] Fetched {len(articles)} articles")

        # Open database
        db = SessionLocal()

        count = 0

        for article_data in articles:

            article_url = clean_url(article_data.get("url", ""))

            # Skip articles without URLs
            if not article_url:
                continue

            # Skip articles already in database
            existing = (
                db.query(Article)
                .filter(Article.url == article_url)
                .first()
            )

            if existing:
                continue

            title = article_data.get("title", "")
            description = article_data.get("description", "")








            # Skip articles without useful descriptions
            if not description or len(description) < 50:
                continue

            try:
                # Generate summary using Groq
                summary = summarize_with_groq(
                    title,
                    description
                )
                category = categorize_article(title, summary)

                # Don't save failed summaries
                if summary == "Summary unavailable":
                    continue

                # Create database record
                article = Article(
                    title=title,
                    summary=summary,
                    category=category,
                    url=article_url,
                    source=article_data.get("source", {}).get("name", ""),
                    image_url=clean_url(article_data.get("urlToImage", "")),
                    published_at=(
                        datetime.fromisoformat(
                            article_data.get("publishedAt", "").replace(
                                "Z", "+00:00"
                            )
                        )
                        if article_data.get("publishedAt")
                        else datetime.utcnow()
                    ),
                )

                db.add(article)
                count += 1

            except Exception as e:
                print(f"[SCHEDULER] Error processing article: {e}")
                continue

        db.commit()

        print(f"[SCHEDULER] Saved {count} new articles")

    except Exception as e:
        print(f"[SCHEDULER] Error: {e}")

        if db:
            db.rollback()

    finally:
        if db:
            db.close()


def start_scheduler():
    """Start background scheduler."""

    scheduler = BackgroundScheduler()

    scheduler.add_job(
        scheduled_fetch_news,
        IntervalTrigger(hours=2),
        id="fetch_news",
        name="Fetch and summarize news",
        replace_existing=True,
    )

    scheduler.start()

    print("[SCHEDULER] Started - will fetch news every 2 hours")

    return scheduler