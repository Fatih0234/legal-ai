from __future__ import annotations

import sqlite3
from datetime import UTC, datetime
from pathlib import Path

DB_PATH = Path("data/cases.db")


def _get_conn() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        """CREATE TABLE IF NOT EXISTS chat_sessions (
            session_id TEXT PRIMARY KEY,
            messages_json TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )"""
    )
    conn.commit()
    return conn


def load(session_id: str) -> bytes | None:
    conn = _get_conn()
    row = conn.execute(
        "SELECT messages_json FROM chat_sessions WHERE session_id = ?",
        (session_id,),
    ).fetchone()
    conn.close()
    return row[0].encode() if row else None


def save(session_id: str, messages_json: bytes) -> None:
    now = datetime.now(tz=UTC).isoformat()
    with _get_conn() as conn:
        conn.execute(
            "INSERT OR REPLACE INTO chat_sessions (session_id, messages_json, updated_at) "
            "VALUES (?, ?, ?)",
            (session_id, messages_json.decode(), now),
        )


def delete(session_id: str) -> None:
    with _get_conn() as conn:
        conn.execute("DELETE FROM chat_sessions WHERE session_id = ?", (session_id,))
