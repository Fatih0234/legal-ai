from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

DB_PATH = Path("data/cache.db")


@dataclass
class CacheEntry:
    url: str
    raw_html: str
    normalized_json: str
    fetched_at: str


def _get_conn() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.execute(
        """CREATE TABLE IF NOT EXISTS cache (
            url TEXT PRIMARY KEY,
            raw_html TEXT NOT NULL,
            normalized_json TEXT NOT NULL,
            fetched_at TEXT NOT NULL
        )"""
    )
    conn.commit()
    return conn


def get(url: str) -> CacheEntry | None:
    conn = _get_conn()
    row = conn.execute(
        "SELECT url, raw_html, normalized_json, fetched_at FROM cache WHERE url = ?",
        (url,),
    ).fetchone()
    conn.close()
    if row is None:
        return None
    return CacheEntry(
        url=row[0], raw_html=row[1], normalized_json=row[2], fetched_at=row[3]
    )


def set(url: str, raw_html: str, normalized_json: str) -> None:
    conn = _get_conn()
    now = datetime.now(tz=UTC).isoformat()
    conn.execute(
        "INSERT OR REPLACE INTO cache (url, raw_html, normalized_json, fetched_at) VALUES (?, ?, ?, ?)",
        (url, raw_html, normalized_json, now),
    )
    conn.commit()
    conn.close()


def has(url: str) -> bool:
    return get(url) is not None


def is_stale(entry: CacheEntry, max_age_days: int = 90) -> bool:
    try:
        fetched = datetime.fromisoformat(entry.fetched_at)
        age = datetime.now(tz=UTC) - fetched
        return age.days > max_age_days
    except (ValueError, TypeError):
        return True
