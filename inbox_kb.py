"""
کیبوردهای اینلاین مربوط به لیست و نمایش جزئیات پیام‌ها (صندوق ورودی و ارسال‌شده‌ها).

پیشوندهای callback_data:
    lopen_{box}_{id}    -> باز کردن پیام از داخل لیست
    lstar_{box}_{id}     -> ستاره‌دار کردن/برداشتن از داخل لیست
    ldelete_{box}_{id}   -> حذف پیام از داخل لیست
    dstar_{box}_{id}     -> ستاره‌دار کردن/برداشتن از صفحه جزئیات
    ddelete_{box}_{id}   -> حذف پیام از صفحه جزئیات
    dback_{box}          -> بازگشت از صفحه جزئیات

box یکی از مقادیر 'inbox' یا 'sent' است.
"""
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def message_list_item_kb(message_id: int, is_starred: bool, box: str) -> InlineKeyboardMarkup:
    star_icon = "⭐" if is_starred else "☆"
    buttons = [
        [
            InlineKeyboardButton(text="📖 باز کردن", callback_data=f"lopen_{box}_{message_id}"),
            InlineKeyboardButton(text=star_icon, callback_data=f"lstar_{box}_{message_id}"),
            InlineKeyboardButton(text="🗑 حذف", callback_data=f"ldelete_{box}_{message_id}"),
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def message_detail_kb(message_id: int, is_starred: bool, box: str) -> InlineKeyboardMarkup:
    star_text = "⭐ حذف ستاره" if is_starred else "☆ ستاره‌دار کردن"
    buttons = [
        [InlineKeyboardButton(text=star_text, callback_data=f"dstar_{box}_{message_id}")],
        [InlineKeyboardButton(text="🗑 حذف پیام", callback_data=f"ddelete_{box}_{message_id}")],
        [InlineKeyboardButton(text="🔙 بازگشت", callback_data=f"dback_{box}")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)
