"""
مدیریت اتصال به دیتابیس SQLite و ساخت جدول‌ها.
از aiosqlite برای عملکرد ناهمزمان (async) استفاده می‌شود.
"""
import os
import aiosqlite

from config.settings import DB_PATH

# اسکریمای کامل دیتابیس
SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    bio TEXT DEFAULT '',
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS sessions (
    telegram_id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    logged_in_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS addresses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    address TEXT UNIQUE NOT NULL,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sender_address TEXT NOT NULL,
    recipient_address TEXT NOT NULL,
    subject TEXT DEFAULT '',
    body TEXT DEFAULT '',
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    is_read INTEGER DEFAULT 0,
    is_starred INTEGER DEFAULT 0,
    deleted_by_sender INTEGER DEFAULT 0,
    deleted_by_recipient INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS attachments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    message_id INTEGER NOT NULL,
    file_type TEXT NOT NULL,
    file_name TEXT,
    telegram_file_id TEXT NOT NULL,
    local_path TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (message_id) REFERENCES messages(id) ON DELETE CASCADE
);
"""


def get_db() -> aiosqlite.Connection:
    """یک اتصال جدید به دیتابیس برمی‌گرداند (به صورت async context manager استفاده شود)."""
    return aiosqlite.connect(DB_PATH)


async def init_db() -> None:
    """پوشه و فایل دیتابیس و جدول‌ها را در صورت نیاز می‌سازد."""
    db_dir = os.path.dirname(DB_PATH)
    if db_dir:
        os.makedirs(db_dir, exist_ok=True)

    async with aiosqlite.connect(DB_PATH) as db:
        await db.executescript(SCHEMA)
        await db.commit()
