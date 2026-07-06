"""
هندلر دستور /start.
همیشه در دسترس است و صرف نظر از وضعیت فعلی، مکالمه را ریست می‌کند.
"""
from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from keyboards.auth_kb import auth_choice_kb
from keyboards.main_menu import main_menu_kb

router = Router(name="start")


@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext, current_user) -> None:
    await state.clear()

    if current_user is not None:
        await message.answer(
            f"👋 خوش آمدید <b>{current_user['username']}</b> عزیز!\n\n"
            "از منوی زیر یکی از گزینه‌ها را انتخاب کنید:",
            reply_markup=main_menu_kb(),
        )
        return

    await message.answer(
        "📨 به <b>PAIL</b> خوش آمدید!\n\n"
        "PAIL یک سامانه پیام‌رسانی خصوصی و شبیه به ایمیل است که فقط درون تلگرام کار می‌کند.\n"
        "برای شروع، ثبت‌نام کنید یا اگر قبلاً حساب دارید وارد شوید:",
        reply_markup=auth_choice_kb(),
    )
