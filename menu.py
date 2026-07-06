"""
هندلر عمومی (fallback) برای پیام‌های متنی که با هیچ‌کدام از دستورات دیگر مطابقت ندارند.
این روتر باید همیشه آخرین روتر ثبت‌شده باشد.
"""
from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from keyboards.auth_kb import auth_choice_kb
from keyboards.main_menu import main_menu_kb

router = Router(name="menu")


@router.message()
async def fallback_handler(message: Message, state: FSMContext, current_user) -> None:
    """اگر پیام کاربر با هیچ هندلری مطابقت نداشت، این پیام نمایش داده می‌شود."""
    current_state = await state.get_state()

    if current_state is not None:
        # کاربر در وسط یک مکالمه چند مرحله‌ای است؛ پیام او فرمت درستی نداشت.
        await message.answer("❗ ورودی نامعتبر است. لطفاً دوباره تلاش کنید یا «❌ انصراف» را بزنید.")
        return

    if current_user is not None:
        await message.answer(
            "❓ متوجه نشدم. لطفاً یکی از گزینه‌های منو را انتخاب کنید:",
            reply_markup=main_menu_kb(),
        )
    else:
        await message.answer(
            "❓ متوجه نشدم. لطفاً ثبت‌نام کنید یا وارد شوید:",
            reply_markup=auth_choice_kb(),
        )
