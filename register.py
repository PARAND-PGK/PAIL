"""
هندلرهای مربوط به فرآیند ثبت‌نام کاربر جدید.
مراحل: نام کاربری -> رمز عبور -> تکرار رمز عبور -> ساخت اولین آدرس PAIL.
"""
from aiogram import F, Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from keyboards.auth_kb import auth_choice_kb, cancel_kb
from keyboards.main_menu import main_menu_kb
from middlewares.auth_middleware import IsGuest
from models.states import RegisterStates
from services.address_service import address_exists, create_address
from services.auth_service import create_session, create_user, username_exists
from utils.validators import (
    is_valid_full_address,
    is_valid_password,
    is_valid_username,
    normalize_address,
)

router = Router(name="register")


@router.message(F.text == "❌ انصراف", StateFilter(
    RegisterStates.username,
    RegisterStates.password,
    RegisterStates.confirm_password,
    RegisterStates.address,
))
async def cancel_registration(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer("ثبت‌نام لغو شد.", reply_markup=auth_choice_kb())


@router.message(F.text == "✅ ثبت‌نام", IsGuest(), StateFilter(None))
async def start_registration(message: Message, state: FSMContext) -> None:
    await state.set_state(RegisterStates.username)
    await message.answer(
        "📝 <b>ثبت‌نام در PAIL</b>\n\n"
        "لطفاً یک نام کاربری انتخاب کنید (فقط حروف انگلیسی، عدد و آندرلاین، بین ۳ تا ۳۲ کاراکتر):",
        reply_markup=cancel_kb(),
    )


@router.message(RegisterStates.username)
async def process_username(message: Message, state: FSMContext) -> None:
    username = (message.text or "").strip()

    if not is_valid_username(username):
        await message.answer(
            "❌ نام کاربری نامعتبر است.\n"
            "فقط حروف انگلیسی، عدد و آندرلاین مجاز است (بین ۳ تا ۳۲ کاراکتر). دوباره وارد کنید:"
        )
        return

    if await username_exists(username):
        await message.answer("❌ این نام کاربری قبلاً استفاده شده است. یک نام کاربری دیگر وارد کنید:")
        return

    await state.update_data(username=username)
    await state.set_state(RegisterStates.password)
    await message.answer("🔑 حالا یک رمز عبور انتخاب کنید (حداقل ۶ کاراکتر):")


@router.message(RegisterStates.password)
async def process_password(message: Message, state: FSMContext) -> None:
    password = message.text or ""

    if not is_valid_password(password):
        await message.answer("❌ رمز عبور باید حداقل ۶ کاراکتر باشد. دوباره وارد کنید:")
        return

    await state.update_data(password=password)
    await state.set_state(RegisterStates.confirm_password)
    await message.answer("🔑 برای تأیید، رمز عبور را دوباره وارد کنید:")


@router.message(RegisterStates.confirm_password)
async def process_confirm_password(message: Message, state: FSMContext) -> None:
    confirm_password = message.text or ""
    data = await state.get_data()

    if confirm_password != data.get("password"):
        await message.answer("❌ رمزهای عبور یکسان نیستند. لطفاً رمز عبور را دوباره وارد کنید:")
        await state.set_state(RegisterStates.password)
        return

    username = data["username"]
    password = data["password"]

    user_id = await create_user(username, password)
    await create_session(message.from_user.id, user_id)

    await state.update_data(user_id=user_id)
    await state.set_state(RegisterStates.address)
    await message.answer(
        "✅ ثبت‌نام با موفقیت انجام شد!\n\n"
        "📮 حالا باید حداقل یک آدرس PAIL برای خودتان بسازید.\n"
        "فقط بخش قبل از @ را وارد کنید، مثلاً: <code>ali</code>\n"
        "آدرس نهایی شما به شکل <code>ali@pail.com</code> خواهد بود.",
    )


@router.message(RegisterStates.address)
async def process_first_address(message: Message, state: FSMContext) -> None:
    raw = (message.text or "").strip()
    address = normalize_address(raw)

    if not is_valid_full_address(address):
        await message.answer(
            "❌ آدرس نامعتبر است. فقط از حروف انگلیسی، عدد، نقطه و آندرلاین استفاده کنید. دوباره وارد کنید:"
        )
        return

    if await address_exists(address):
        await message.answer(f"❌ آدرس <code>{address}</code> قبلاً استفاده شده است. یک آدرس دیگر وارد کنید:")
        return

    data = await state.get_data()
    await create_address(data["user_id"], address)
    await state.clear()

    await message.answer(
        f"🎉 آدرس <code>{address}</code> با موفقیت ساخته شد!\n\n"
        "حالا می‌توانید از منوی زیر استفاده کنید:",
        reply_markup=main_menu_kb(),
    )
