import sqlite3
import json
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env
PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")

DEFAULT_DB_PATH = PROJECT_ROOT / "data" / "papers.db"
DB_PATH = Path(os.getenv("DB_PATH", DEFAULT_DB_PATH)).resolve()


def get_connection():
    """Ensure the data directory exists and return a SQLite connection."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Allows accessing columns by name
    return conn


def init_db():
    """Initialize the papers table if it does not exist."""
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS papers (
                filename TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                summary TEXT NOT NULL,
                keywords TEXT NOT NULL,
                category TEXT NOT NULL,
                processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()


def get_processed_filenames() -> set[str]:
    """Return a set of all filenames already stored in the database."""
    init_db()
    with get_connection() as conn:
        cursor = conn.execute("SELECT filename FROM papers")
        return {row["filename"] for row in cursor.fetchall()}


def insert_paper(filename: str, metadata: dict):
    """
    Insert or update a paper record in SQLite.
    Expects metadata dict with keys: title, summary, keywords (list), category.
    """
    init_db()
    keywords_json = json.dumps(metadata.get("keywords", []))
    with get_connection() as conn:
        conn.execute("""
            INSERT OR REPLACE INTO papers (filename, title, summary, keywords, category)
            VALUES (?, ?, ?, ?, ?)
        """, (
            filename,
            metadata["title"],
            metadata["summary"],
            keywords_json,
            metadata["category"]
        ))
        conn.commit()


def get_all_papers() -> list[dict]:
    """Retrieve all papers ordered by most recently processed (used for HTML generation)."""
    init_db()
    with get_connection() as conn:
        cursor = conn.execute("SELECT * FROM papers ORDER BY processed_at DESC")
        rows = cursor.fetchall()
        papers = []
        for row in rows:
            paper = dict(row)
            paper["keywords"] = json.loads(paper["keywords"])
            papers.append(paper)
        return papers


if __name__ == "__main__":
    # Quick sanity check when run directly from terminal
    init_db()
    print(f"Database successfully initialized at: {DB_PATH}")