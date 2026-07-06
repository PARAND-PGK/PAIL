"""
کیبورد اصلی منو (پس از ورود موفق).
"""
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def main_menu_kb() -> ReplyKeyboardMarkup:
    keyboard = [
        [KeyboardButton(text="📥 صندوق ورودی"), KeyboardButton(text="📤 ارسال‌شده‌ها")],
        [KeyboardButton(text="➕ پیام جدید")],
        [KeyboardButton(text="👤 پروفایل"), KeyboardButton(text="⚙ تنظیمات")],
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)
