"""SQLite database setup and helpers."""

import aiosqlite
import os
import secrets
import hashlib
from datetime import datetime, timezone

DB_PATH = os.getenv("PDF_API_DB", "pdf_api.db")


async def get_db() -> aiosqlite.Connection:
    db = await aiosqlite.connect(DB_PATH)
    db.row_factory = aiosqlite.Row
    return db


async def init_db():
    """Initialize database tables."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS api_keys (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key_hash TEXT UNIQUE NOT NULL,
                key_prefix TEXT NOT NULL,
                plan TEXT NOT NULL DEFAULT 'free',
                email TEXT,
                created_at TEXT NOT NULL,
                active INTEGER NOT NULL DEFAULT 1
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS usage_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key_hash TEXT,
                ip_address TEXT,
                endpoint TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                month_key TEXT NOT NULL
            )
        """)
        await db.execute("""
            CREATE INDEX IF NOT EXISTS idx_usage_month
            ON usage_log(key_hash, month_key)
        """)
        await db.execute("""
            CREATE INDEX IF NOT EXISTS idx_usage_ip_month
            ON usage_log(ip_address, month_key)
        """)
        await db.commit()


def hash_key(api_key: str) -> str:
    return hashlib.sha256(api_key.encode()).hexdigest()


def get_month_key() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m")


async def generate_api_key(plan: str = "free", email: str = None) -> str:
    """Generate a new API key and store it."""
    raw_key = f"epf_{secrets.token_urlsafe(32)}"
    key_h = hash_key(raw_key)
    prefix = raw_key[:12]

    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO api_keys (key_hash, key_prefix, plan, email, created_at) VALUES (?, ?, ?, ?, ?)",
            (key_h, prefix, plan, email, datetime.now(timezone.utc).isoformat()),
        )
        await db.commit()
    return raw_key


async def get_key_info(api_key: str) -> dict | None:
    """Look up API key info."""
    key_h = hash_key(api_key)
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT * FROM api_keys WHERE key_hash = ? AND active = 1", (key_h,)
        )
        row = await cursor.fetchone()
        if row:
            return dict(row)
    return None


async def log_usage(key_hash: str | None, ip: str, endpoint: str):
    """Log an API call."""
    now = datetime.now(timezone.utc)
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO usage_log (key_hash, ip_address, endpoint, timestamp, month_key) VALUES (?, ?, ?, ?, ?)",
            (key_hash, ip, endpoint, now.isoformat(), get_month_key()),
        )
        await db.commit()


async def get_usage_count(key_hash: str | None, ip: str | None) -> int:
    """Get usage count for current month."""
    month = get_month_key()
    async with aiosqlite.connect(DB_PATH) as db:
        if key_hash:
            cursor = await db.execute(
                "SELECT COUNT(*) FROM usage_log WHERE key_hash = ? AND month_key = ?",
                (key_hash, month),
            )
        else:
            cursor = await db.execute(
                "SELECT COUNT(*) FROM usage_log WHERE ip_address = ? AND key_hash IS NULL AND month_key = ?",
                (ip, month),
            )
        row = await cursor.fetchone()
        return row[0] if row else 0
