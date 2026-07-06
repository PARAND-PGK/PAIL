"""
کیبوردهای اینلاین مربوط به فرآیند ساخت و ارسال پیام جدید.
"""
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def sender_choice_kb(addresses: list[str]) -> InlineKeyboardMarkup:
    """لیست آدرس‌های خود کاربر برای انتخاب آدرس فرستنده."""
    buttons = [
        [InlineKeyboardButton(text=address, callback_data=f"choose_sender_{address}")]
        for address in addresses
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def attachment_kb(count: int = 0) -> InlineKeyboardMarkup:
    """کیبورد نمایش‌داده‌شده در حین افزودن پیوست‌ها به پیام جدید."""
    send_text = f"✅ ارسال پیام ({count} پیوست)" if count else "✅ ارسال پیام"
    buttons = [
        [InlineKeyboardButton(text=send_text, callback_data="send_message_final")],
        [InlineKeyboardButton(text="❌ انصراف از ارسال", callback_data="cancel_new_message")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)
