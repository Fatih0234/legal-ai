from __future__ import annotations

import hashlib
import sqlite3
from datetime import UTC, datetime
from pathlib import Path

DB_PATH = Path("data/cases.db")


def _get_conn() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        """CREATE TABLE IF NOT EXISTS progress (
            case_id TEXT NOT NULL,
            step_key TEXT NOT NULL,
            step_text TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'PENDING',
            updated_at TEXT NOT NULL,
            PRIMARY KEY (case_id, step_key)
        )"""
    )
    conn.commit()
    return conn


def _step_key(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()[:12]


def init_case(case_id: str, steps: list[str]) -> None:
    """Insert PENDING rows for each step if they don't exist yet."""
    now = datetime.now(tz=UTC).isoformat()
    with _get_conn() as conn:
        for text in steps:
            key = _step_key(text)
            conn.execute(
                "INSERT OR IGNORE INTO progress (case_id, step_key, step_text, status, updated_at) "
                "VALUES (?, ?, ?, 'PENDING', ?)",
                (case_id, key, text, now),
            )


def upsert(case_id: str, step_key: str, status: str) -> bool:
    """Update status for a step. Returns False if step_key not found."""
    now = datetime.now(tz=UTC).isoformat()
    with _get_conn() as conn:
        cur = conn.execute(
            "UPDATE progress SET status = ?, updated_at = ? WHERE case_id = ? AND step_key = ?",
            (status, now, case_id, step_key),
        )
        return cur.rowcount > 0


def get_all(case_id: str) -> list[dict]:
    conn = _get_conn()
    rows = conn.execute(
        "SELECT step_key, step_text, status, updated_at FROM progress WHERE case_id = ? ORDER BY rowid",
        (case_id,),
    ).fetchall()
    conn.close()
    return [
        {"step_key": r[0], "step_text": r[1], "status": r[2], "updated_at": r[3]}
        for r in rows
    ]
