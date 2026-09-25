# Held-out eval tracking (concept fix: practice leaks into assessment).
# Every served practice question is logged by text hash. Graded evals sample
# only unseen questions, so eval scores measure knowledge, not exposure.
# Additive table; v1 flows never read it.

import hashlib
import sqlite3
from datetime import datetime, timezone

SEEN_DB = "./onboardiq.db"


def qhash(question_text: str) -> str:
    return hashlib.sha256((question_text or "").strip().lower().encode("utf-8")).hexdigest()[:16]


def _ensure_table(conn: sqlite3.Connection) -> None:
    conn.execute(
        """CREATE TABLE IF NOT EXISTS user_seen_questions (
            user_id TEXT,
            qhash TEXT,
            seen_at TEXT,
            PRIMARY KEY (user_id, qhash)
        )"""
    )


def log_seen(user_id: str, question_texts) -> int:
    """Record served questions. Idempotent. Returns new rows added."""
    texts = [t for t in (question_texts or []) if t]
    if not user_id or not texts:
        return 0
    now = datetime.now(timezone.utc).isoformat()
    conn = sqlite3.connect(SEEN_DB)
    try:
        _ensure_table(conn)
        added = conn.executemany(
            "INSERT OR IGNORE INTO user_seen_questions (user_id, qhash, seen_at) VALUES (?, ?, ?)",
            [(user_id, qhash(t), now) for t in texts],
        ).rowcount
        conn.commit()
        return added or 0
    finally:
        conn.close()


def get_seen_hashes(user_id: str) -> set:
    if not user_id:
        return set()
    conn = sqlite3.connect(SEEN_DB)
    try:
        _ensure_table(conn)
        return {r[0] for r in conn.execute(
            "SELECT qhash FROM user_seen_questions WHERE user_id = ?", (user_id,))}
    finally:
        conn.close()
