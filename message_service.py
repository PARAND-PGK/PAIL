"""
سرویس مربوط به مدیریت پیام‌ها: ساخت، دریافت صندوق ورودی/ارسال‌شده،
حذف، ستاره‌دار کردن و مدیریت پیوست‌ها.
"""
import aiosqlite

from database.db import get_db


async def create_message(sender_address: str, recipient_address: str, subject: str, body: str) -> int:
    async with get_db() as db:
        cursor = await db.execute(
            """
            INSERT INTO messages (sender_address, recipient_address, subject, body)
            VALUES (?, ?, ?, ?)
            """,
            (sender_address, recipient_address, subject, body),
        )
        await db.commit()
        return cursor.lastrowid


async def add_attachment(message_id: int, file_type: str, file_name: str,
                          telegram_file_id: str, local_path: str) -> None:
    async with get_db() as db:
        await db.execute(
            """
            INSERT INTO attachments (message_id, file_type, file_name, telegram_file_id, local_path)
            VALUES (?, ?, ?, ?, ?)
            """,
            (message_id, file_type, file_name, telegram_file_id, local_path),
        )
        await db.commit()


async def get_attachments(message_id: int):
    async with get_db() as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM attachments WHERE message_id = ?", (message_id,))
        return await cursor.fetchall()


async def get_inbox(addresses: list[str]):
    """پیام‌های دریافتی برای مجموعه‌ای از آدرس‌های کاربر (جدیدترین اول)."""
    if not addresses:
        return []
    placeholders = ",".join("?" * len(addresses))
    async with get_db() as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            f"""
            SELECT * FROM messages
            WHERE recipient_address IN ({placeholders}) AND deleted_by_recipient = 0
            ORDER BY created_at DESC
            """,
            addresses,
        )
        return await cursor.fetchall()


async def get_sent(addresses: list[str]):
    """پیام‌های ارسال‌شده از مجموعه‌ای از آدرس‌های کاربر (جدیدترین اول)."""
    if not addresses:
        return []
    placeholders = ",".join("?" * len(addresses))
    async with get_db() as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            f"""
            SELECT * FROM messages
            WHERE sender_address IN ({placeholders}) AND deleted_by_sender = 0
            ORDER BY created_at DESC
            """,
            addresses,
        )
        return await cursor.fetchall()


async def get_message_by_id(message_id: int):
    async with get_db() as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM messages WHERE id = ?", (message_id,))
        return await cursor.fetchone()


async def mark_as_read(message_id: int) -> None:
    async with get_db() as db:
        await db.execute("UPDATE messages SET is_read = 1 WHERE id = ?", (message_id,))
        await db.commit()


async def toggle_star(message_id: int) -> bool | None:
    """وضعیت ستاره‌دار بودن پیام را برعکس می‌کند و مقدار جدید را برمی‌گرداند."""
    async with get_db() as db:
        cursor = await db.execute("SELECT is_starred FROM messages WHERE id = ?", (message_id,))
        row = await cursor.fetchone()
        if row is None:
            return None
        new_value = 0 if row[0] else 1
        await db.execute("UPDATE messages SET is_starred = ? WHERE id = ?", (new_value, message_id))
        await db.commit()
        return bool(new_value)


async def delete_message_for_sender(message_id: int) -> None:
    async with get_db() as db:
        await db.execute("UPDATE messages SET deleted_by_sender = 1 WHERE id = ?", (message_id,))
        await db.commit()


async def delete_message_for_recipient(message_id: int) -> None:
    async with get_db() as db:
        await db.execute("UPDATE messages SET deleted_by_recipient = 1 WHERE id = ?", (message_id,))
        await db.commit()
