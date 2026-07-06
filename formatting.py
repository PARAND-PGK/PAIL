"""
توابع کمکی برای قالب‌بندی متن‌ها و تاریخ‌ها برای نمایش به کاربر.
"""
from datetime import datetime


def format_datetime(raw_datetime: str) -> str:
    """رشته تاریخ ذخیره‌شده در دیتابیس را به شکل خوانا تبدیل می‌کند."""
    try:
        dt = datetime.strptime(raw_datetime, "%Y-%m-%d %H:%M:%S")
    except (ValueError, TypeError):
        return raw_datetime or "-"
    return dt.strftime("%Y/%m/%d - %H:%M")


def truncate(text: str, max_length: int = 60) -> str:
    """متن طولانی را برای نمایش خلاصه کوتاه می‌کند."""
    text = text or ""
    if len(text) <= max_length:
        return text
    return text[:max_length].rstrip() + " ..."
