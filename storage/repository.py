from storage.db import get_connection


class ArticleRepository:
    def exists(self, url: str) -> bool:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT 1 FROM articles WHERE url = ?",
            (url,)
        )

        result = cursor.fetchone()
        conn.close()

        return result is not None

    def save(self, title, url, summary, published_at):
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO articles (title, url, summary, published_at)
            VALUES (?, ?, ?, ?)
        """, (title, url, summary, published_at))

        conn.commit()
        conn.close()

    def fetch_latest(self, limit=10, offset=0):
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT title, summary, published_at
            FROM articles
            ORDER BY created_at DESC
            LIMIT ? OFFSET ?
        """, (limit, offset))

        rows = cursor.fetchall()
        conn.close()

        return rows
