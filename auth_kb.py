"""
کیبوردهای مربوط به مراحل ثبت‌نام و ورود.
"""
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def auth_choice_kb() -> ReplyKeyboardMarkup:
    """کیبورد انتخاب بین ثبت‌نام و ورود."""
    keyboard = [
        [KeyboardButton(text="✅ ثبت‌نام"), KeyboardButton(text="✅ ورود")],
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)


def cancel_kb() -> ReplyKeyboardMarkup:
    """کیبورد ساده برای انصراف از مراحل چند قسمتی."""
    keyboard = [[KeyboardButton(text="❌ انصراف")]]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)
