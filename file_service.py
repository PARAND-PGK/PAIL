"""
سرویس مربوط به دانلود و ذخیره فایل‌های پیوست در فضای ذخیره‌سازی محلی (storage/).
"""
import os

from aiogram import Bot

from config.settings import STORAGE_PATH


async def save_attachment_file(bot: Bot, file_id: str, message_id: int, file_name: str) -> str:
    """
    فایل تلگرامی را دانلود کرده و در پوشه محلی storage/attachments/<message_id>/ ذخیره می‌کند.
    مسیر محلی ذخیره‌شده را برمی‌گرداند.
    """
    folder = os.path.join(STORAGE_PATH, str(message_id))
    os.makedirs(folder, exist_ok=True)

    safe_name = file_name or file_id
    local_path = os.path.join(folder, safe_name)

    telegram_file = await bot.get_file(file_id)
    await bot.download_file(telegram_file.file_path, destination=local_path)

    return local_path
