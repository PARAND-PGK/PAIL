"""
هندلرهای مربوط به فرآیند ورود (Login) کاربر.
مراحل: نام کاربری -> رمز عبور -> بررسی صحت و ساخت نشست (session).
"""
from aiogram import F, Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from keyboards.auth_kb import auth_choice_kb, cancel_kb
from keyboards.main_menu import main_menu_kb
from middlewares.auth_middleware import IsGuest
from models.states import LoginStates
from services.auth_service import authenticate_user, create_session

router = Router(name="login")


@router.message(F.text == "❌ انصراف", StateFilter(LoginStates.username, LoginStates.password))
async def cancel_login(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer("ورود لغو شد.", reply_markup=auth_choice_kb())


@router.message(F.text == "✅ ورود", IsGuest(), StateFilter(None))
async def start_login(message: Message, state: FSMContext) -> None:
    await state.set_state(LoginStates.username)
    await message.answer("👤 نام کاربری خود را وارد کنید:", reply_markup=cancel_kb())


@router.message(LoginStates.username)
async def process_login_username(message: Message, state: FSMContext) -> None:
    username = (message.text or "").strip()
    await state.update_data(username=username)
    await state.set_state(LoginStates.password)
    await message.answer("🔑 رمز عبور خود را وارد کنید:")


@router.message(LoginStates.password)
async def process_login_password(message: Message, state: FSMContext) -> None:
    password = message.text or ""
    data = await state.get_data()
    username = data.get("username", "")

    user = await authenticate_user(username, password)

    if user is None:
        await state.clear()
        await message.answer(
            "❌ نام کاربری یا رمز عبور اشتباه است.\n"
            "لطفاً دوباره تلاش کنید:",
            reply_markup=auth_choice_kb(),
        )
        return

    await create_session(message.from_user.id, user["id"])
    await state.clear()

    await message.answer(
        f"✅ خوش آمدید <b>{user['username']}</b> عزیز!\n\nاز منوی زیر استفاده کنید:",
        reply_markup=main_menu_kb(),
    )
