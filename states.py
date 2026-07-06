"""
گروه‌های وضعیت (FSM States) برای مکالمات چند مرحله‌ای ربات.
"""
from aiogram.fsm.state import State, StatesGroup


class RegisterStates(StatesGroup):
    """مراحل ثبت‌نام کاربر جدید."""
    username = State()
    password = State()
    confirm_password = State()
    address = State()


class LoginStates(StatesGroup):
    """مراحل ورود کاربر."""
    username = State()
    password = State()


class NewAddressStates(StatesGroup):
    """مرحله ساخت آدرس جدید در تنظیمات."""
    address = State()


class DeleteAddressStates(StatesGroup):
    """مرحله حذف آدرس در تنظیمات."""
    select = State()


class ChangePasswordStates(StatesGroup):
    """مراحل تغییر رمز عبور."""
    old_password = State()
    new_password = State()
    confirm_password = State()


class NewMessageStates(StatesGroup):
    """مراحل ارسال پیام جدید."""
    choose_sender = State()
    recipient = State()
    subject = State()
    body = State()
    attachments = State()
