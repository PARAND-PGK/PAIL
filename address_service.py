"""
سرویس مربوط به مدیریت آدرس‌های PAIL (ساخت، حذف، جستجو).
"""
import aiosqlite

from database.db import get_db


async def address_exists(address: str) -> bool:
    async with get_db() as db:
        cursor = await db.execute("SELECT 1 FROM addresses WHERE address = ?", (address,))
        row = await cursor.fetchone()
        return row is not None


async def create_address(user_id: int, address: str) -> int:
    async with get_db() as db:
        cursor = await db.execute(
            "INSERT INTO addresses (user_id, address) VALUES (?, ?)",
            (user_id, address),
        )
        await db.commit()
        return cursor.lastrowid


async def get_addresses_for_user(user_id: int):
    async with get_db() as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT * FROM addresses WHERE user_id = ? ORDER BY created_at ASC",
            (user_id,),
        )
        return await cursor.fetchall()


async def get_address_owner(address: str):
    """رکورد آدرس (شامل user_id مالک) را برمی‌گرداند، در صورت نبود None."""
    async with get_db() as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM addresses WHERE address = ?", (address,))
        return await cursor.fetchone()


async def delete_address(user_id: int, address: str) -> bool:
    async with get_db() as db:
        cursor = await db.execute(
            "DELETE FROM addresses WHERE user_id = ? AND address = ?",
            (user_id, address),
        )
        await db.commit()
        return cursor.rowcount > 0


async def count_addresses(user_id: int) -> int:
    async with get_db() as db:
        cursor = await db.execute("SELECT COUNT(*) FROM addresses WHERE user_id = ?", (user_id,))
        row = await cursor.fetchone()
        return row[0] if row else 0
