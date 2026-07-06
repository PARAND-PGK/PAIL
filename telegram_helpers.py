"""
توابع کمکی مرتبط با تلگرام: تشخیص نوع فایل پیوست و ارسال دوباره آن.
"""
from aiogram import Bot
from aiogram.types import Message


def extract_file_info(message: Message):
    """
    نوع فایل، file_id و نام فایل را از یک پیام تلگرامی استخراج می‌کند.
    خروجی: (file_type, file_id, file_name) یا (None, None, None)
    """
    if message.photo:
        photo = message.photo[-1]
        return "photo", photo.file_id, f"photo_{photo.file_unique_id}.jpg"

    if message.video:
        video = message.video
        return "video", video.file_id, video.file_name or f"video_{video.file_unique_id}.mp4"

    if message.audio:
        audio = message.audio
        return "audio", audio.file_id, audio.file_name or f"audio_{audio.file_unique_id}.mp3"

    if message.voice:
        voice = message.voice
        return "voice", voice.file_id, f"voice_{voice.file_unique_id}.ogg"

    if message.document:
        document = message.document
        return "document", document.file_id, document.file_name or f"file_{document.file_unique_id}"

    return None, None, None


async def send_attachment(bot: Bot, chat_id: int, attachment) -> None:
    """یک پیوست ذخیره‌شده را با استفاده از telegram_file_id دوباره برای کاربر ارسال می‌کند."""
    file_id = attachment["telegram_file_id"]
    file_type = attachment["file_type"]
    caption = attachment["file_name"] or ""

    if file_type == "photo":
        await bot.send_photo(chat_id, file_id, caption=caption)
    elif file_type == "video":
        await bot.send_video(chat_id, file_id, caption=caption)
    elif file_type == "audio":
        await bot.send_audio(chat_id, file_id, caption=caption)
    elif file_type == "voice":
        await bot.send_voice(chat_id, file_id, caption=caption)
    else:
        await bot.send_document(chat_id, file_id, caption=caption)
