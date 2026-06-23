"""SQLite helpers — schema creation and CRUD for reviews."""

import sqlite3
import contextlib
from . import config

DDL = """
CREATE TABLE IF NOT EXISTS reviews (
    review_id    TEXT PRIMARY KEY,
    author       TEXT,
    star_rating  INTEGER,
    comment      TEXT,
    created_at   TEXT,
    draft_reply  TEXT,
    status       TEXT NOT NULL DEFAULT 'new',
    final_reply  TEXT,
    posted_at    TEXT,
    sensitive    INTEGER NOT NULL DEFAULT 0
);
"""


@contextlib.contextmanager
def get_conn():
    conn = sqlite3.connect(config.DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db():
    with get_conn() as conn:
        conn.executescript(DDL)


def known_ids() -> set[str]:
    with get_conn() as conn:
        rows = conn.execute("SELECT review_id FROM reviews").fetchall()
    return {r["review_id"] for r in rows}


def insert_review(review: dict) -> None:
    with get_conn() as conn:
        conn.execute(
            """INSERT OR IGNORE INTO reviews
               (review_id, author, star_rating, comment, created_at, sensitive)
               VALUES (:review_id, :author, :star_rating, :comment, :created_at, :sensitive)""",
            review,
        )


def save_draft(review_id: str, draft: str, sensitive: bool) -> None:
    with get_conn() as conn:
        conn.execute(
            """UPDATE reviews
               SET draft_reply = ?, status = 'drafted', sensitive = ?
               WHERE review_id = ?""",
            (draft, int(sensitive), review_id),
        )


def get_reviews(status: str | None = None) -> list[sqlite3.Row]:
    with get_conn() as conn:
        if status:
            rows = conn.execute(
                "SELECT * FROM reviews WHERE status = ? ORDER BY created_at DESC", (status,)
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM reviews ORDER BY created_at DESC"
            ).fetchall()
    return rows


def get_review(review_id: str) -> sqlite3.Row | None:
    with get_conn() as conn:
        return conn.execute(
            "SELECT * FROM reviews WHERE review_id = ?", (review_id,)
        ).fetchone()


def set_status(review_id: str, status: str, final_reply: str | None = None, posted_at: str | None = None) -> None:
    with get_conn() as conn:
        conn.execute(
            """UPDATE reviews
               SET status = ?, final_reply = COALESCE(?, final_reply), posted_at = COALESCE(?, posted_at)
               WHERE review_id = ?""",
            (status, final_reply, posted_at, review_id),
        )
