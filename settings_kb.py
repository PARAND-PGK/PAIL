"""
کیبورد منوی تنظیمات.
"""
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def settings_menu_kb() -> ReplyKeyboardMarkup:
    keyboard = [
        [KeyboardButton(text="🔑 تغییر رمز عبور")],
        [KeyboardButton(text="➕ ساخت آدرس جدید"), KeyboardButton(text="🗑 حذف آدرس")],
        [KeyboardButton(text="🚪 خروج از حساب")],
        [KeyboardButton(text="🔙 بازگشت به منو")],
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)
