"""
سرویس مربوط به احراز هویت: ثبت‌نام، ورود، نشست (session) و تغییر رمز عبور.
"""
import aiosqlite

from database.db import get_db
from utils.security import hash_password, verify_password


async def get_user_by_username(username: str):
    async with get_db() as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM users WHERE username = ?", (username,))
        return await cursor.fetchone()


async def get_user_by_id(user_id: int):
    async with get_db() as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        return await cursor.fetchone()


async def username_exists(username: str) -> bool:
    user = await get_user_by_username(username)
    return user is not None


async def create_user(username: str, password: str) -> int:
    """کاربر جدید می‌سازد و شناسه آن را برمی‌گرداند."""
    password_hash = hash_password(password)
    async with get_db() as db:
        cursor = await db.execute(
            "INSERT INTO users (username, password_hash) VALUES (?, ?)",
            (username, password_hash),
        )
        await db.commit()
        return cursor.lastrowid


async def authenticate_user(username: str, password: str):
    """در صورت صحت نام کاربری و رمز عبور، رکورد کاربر را برمی‌گرداند وگرنه None."""
    user = await get_user_by_username(username)
    if user is None:
        return None
    if not verify_password(password, user["password_hash"]):
        return None
    return user


async def change_password(user_id: int, new_password: str) -> None:
    password_hash = hash_password(new_password)
    async with get_db() as db:
        await db.execute("UPDATE users SET password_hash = ? WHERE id = ?", (password_hash, user_id))
        await db.commit()


async def create_session(telegram_id: int, user_id: int) -> None:
    """کاربر تلگرامی را به یک حساب PAIL متصل (لاگین) می‌کند."""
    async with get_db() as db:
        await db.execute(
            """
            INSERT INTO sessions (telegram_id, user_id, logged_in_at)
            VALUES (?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(telegram_id) DO UPDATE SET
                user_id = excluded.user_id,
                logged_in_at = CURRENT_TIMESTAMP
            """,
            (telegram_id, user_id),
        )
        await db.commit()


async def destroy_session(telegram_id: int) -> None:
    """خروج (logout) کاربر تلگرامی از حساب فعلی."""
    async with get_db() as db:
        await db.execute("DELETE FROM sessions WHERE telegram_id = ?", (telegram_id,))
        await db.commit()


async def get_logged_in_user(telegram_id: int):
    """کاربر لاگین‌شده متصل به یک شناسه تلگرامی را برمی‌گرداند، در غیر این صورت None."""
    async with get_db() as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            """
            SELECT users.* FROM users
            JOIN sessions ON sessions.user_id = users.id
            WHERE sessions.telegram_id = ?
            """,
            (telegram_id,),
        )
        return await cursor.fetchone()


async def get_telegram_ids_by_user_id(user_id: int) -> list[int]:
    """تمام شناسه‌های تلگرامی لاگین‌شده به یک حساب کاربری را برمی‌گرداند."""
    async with get_db() as db:
        cursor = await db.execute("SELECT telegram_id FROM sessions WHERE user_id = ?", (user_id,))
        rows = await cursor.fetchall()
        return [row[0] for row in rows]
