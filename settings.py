"""
هندلرهای مربوط به «تنظیمات»: تغییر رمز عبور، ساخت آدرس جدید، حذف آدرس و خروج از حساب.
"""
from aiogram import F, Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message

from keyboards.auth_kb import auth_choice_kb, cancel_kb
from keyboards.main_menu import main_menu_kb
from keyboards.settings_kb import settings_menu_kb
from middlewares.auth_middleware import IsAuthenticated
from models.states import ChangePasswordStates, NewAddressStates
from services.address_service import (
    address_exists,
    count_addresses,
    create_address,
    delete_address,
    get_addresses_for_user,
)
from services.auth_service import change_password, destroy_session
from utils.security import verify_password
from utils.validators import is_valid_full_address, is_valid_password, normalize_address

router = Router(name="settings")


# ---------------------------------------------------------------------------
# منوی تنظیمات
# ---------------------------------------------------------------------------

@router.message(F.text == "⚙ تنظیمات", IsAuthenticated(), StateFilter(None))
async def show_settings(message: Message) -> None:
    await message.answer("⚙ <b>تنظیمات</b>\n\nیکی از گزینه‌های زیر را انتخاب کنید:", reply_markup=settings_menu_kb())


@router.message(F.text == "🔙 بازگشت به منو", IsAuthenticated(), StateFilter(None))
async def back_to_main_menu(message: Message) -> None:
    await message.answer("به منوی اصلی بازگشتید:", reply_markup=main_menu_kb())


# ---------------------------------------------------------------------------
# انصراف عمومی از هر مرحله تنظیمات
# ---------------------------------------------------------------------------

@router.message(F.text == "❌ انصراف", StateFilter(
    ChangePasswordStates.old_password,
    ChangePasswordStates.new_password,
    ChangePasswordStates.confirm_password,
    NewAddressStates.address,
))
async def cancel_settings_flow(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer("عملیات لغو شد.", reply_markup=settings_menu_kb())


# ---------------------------------------------------------------------------
# تغییر رمز عبور
# ---------------------------------------------------------------------------

@router.message(F.text == "🔑 تغییر رمز عبور", IsAuthenticated(), StateFilter(None))
async def start_change_password(message: Message, state: FSMContext) -> None:
    await state.set_state(ChangePasswordStates.old_password)
    await message.answer("🔑 رمز عبور فعلی خود را وارد کنید:", reply_markup=cancel_kb())


@router.message(ChangePasswordStates.old_password)
async def process_old_password(message: Message, state: FSMContext, current_user) -> None:
    old_password = message.text or ""

    if not verify_password(old_password, current_user["password_hash"]):
        await message.answer("❌ رمز عبور فعلی اشتباه است. دوباره وارد کنید:")
        return

    await state.set_state(ChangePasswordStates.new_password)
    await message.answer("🔑 رمز عبور جدید را وارد کنید (حداقل ۶ کاراکتر):")


@router.message(ChangePasswordStates.new_password)
async def process_new_password(message: Message, state: FSMContext) -> None:
    new_password = message.text or ""

    if not is_valid_password(new_password):
        await message.answer("❌ رمز عبور باید حداقل ۶ کاراکتر باشد. دوباره وارد کنید:")
        return

    await state.update_data(new_password=new_password)
    await state.set_state(ChangePasswordStates.confirm_password)
    await message.answer("🔑 برای تأیید، رمز عبور جدید را دوباره وارد کنید:")


@router.message(ChangePasswordStates.confirm_password)
async def process_confirm_new_password(message: Message, state: FSMContext, current_user) -> None:
    confirm_password = message.text or ""
    data = await state.get_data()

    if confirm_password != data.get("new_password"):
        await message.answer("❌ رمزهای عبور یکسان نیستند. رمز عبور جدید را دوباره وارد کنید:")
        await state.set_state(ChangePasswordStates.new_password)
        return

    await change_password(current_user["id"], confirm_password)
    await state.clear()
    await message.answer("✅ رمز عبور با موفقیت تغییر یافت.", reply_markup=settings_menu_kb())


# ---------------------------------------------------------------------------
# ساخت آدرس جدید
# ---------------------------------------------------------------------------

@router.message(F.text == "➕ ساخت آدرس جدید", IsAuthenticated(), StateFilter(None))
async def start_new_address(message: Message, state: FSMContext) -> None:
    await state.set_state(NewAddressStates.address)
    await message.answer(
        "📮 آدرس دلخواه خود را وارد کنید (فقط بخش قبل از @، مثلاً <code>music</code>):",
        reply_markup=cancel_kb(),
    )


@router.message(NewAddressStates.address)
async def process_new_address(message: Message, state: FSMContext, current_user) -> None:
    raw = (message.text or "").strip()
    address = normalize_address(raw)

    if not is_valid_full_address(address):
        await message.answer("❌ آدرس نامعتبر است. دوباره وارد کنید:")
        return

    if await address_exists(address):
        await message.answer(f"❌ آدرس <code>{address}</code> قبلاً استفاده شده است. یک آدرس دیگر وارد کنید:")
        return

    await create_address(current_user["id"], address)
    await state.clear()
    await message.answer(f"✅ آدرس <code>{address}</code> با موفقیت ساخته شد.", reply_markup=settings_menu_kb())


# ---------------------------------------------------------------------------
# حذف آدرس
# ---------------------------------------------------------------------------

@router.message(F.text == "🗑 حذف آدرس", IsAuthenticated(), StateFilter(None))
async def start_delete_address(message: Message, current_user) -> None:
    addresses = await get_addresses_for_user(current_user["id"])

    if not addresses:
        await message.answer("شما هیچ آدرسی برای حذف ندارید.", reply_markup=settings_menu_kb())
        return

    buttons = [
        [InlineKeyboardButton(text=row["address"], callback_data=f"deladdr_{row['address']}")]
        for row in addresses
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)

    await message.answer("🗑 کدام آدرس حذف شود؟", reply_markup=keyboard)


@router.callback_query(F.data.startswith("deladdr_"))
async def process_delete_address(callback: CallbackQuery, current_user) -> None:
    address = callback.data.removeprefix("deladdr_")

    remaining = await count_addresses(current_user["id"])
    if remaining <= 1:
        await callback.answer(
            "⚠ این آخرین آدرس شماست. در صورت حذف، پیامی دریافت نخواهید کرد.",
            show_alert=True,
        )

    deleted = await delete_address(current_user["id"], address)

    if deleted:
        await callback.message.edit_text(f"✅ آدرس <code>{address}</code> حذف شد.")
    else:
        await callback.message.edit_text("❌ حذف آدرس ممکن نشد.")

    await callback.answer()


# ---------------------------------------------------------------------------
# خروج از حساب
# ---------------------------------------------------------------------------

@router.message(F.text == "🚪 خروج از حساب", IsAuthenticated(), StateFilter(None))
async def logout(message: Message, state: FSMContext) -> None:
    await destroy_session(message.from_user.id)
    await state.clear()
    await message.answer(
        "🚪 شما با موفقیت از حساب خود خارج شدید.\n\nبرای ادامه، ثبت‌نام کنید یا وارد شوید:",
        reply_markup=auth_choice_kb(),
    )
