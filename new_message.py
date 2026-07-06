"""
هندلرهای مربوط به ساخت و ارسال یک پیام جدید:
انتخاب آدرس فرستنده (در صورت داشتن چند آدرس) -> گیرنده -> موضوع -> متن پیام -> پیوست‌ها -> ارسال نهایی.
"""
from aiogram import F, Router
from aiogram.enums import ContentType
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from keyboards.auth_kb import cancel_kb
from keyboards.main_menu import main_menu_kb
from keyboards.message_kb import attachment_kb, sender_choice_kb
from middlewares.auth_middleware import IsAuthenticated
from models.states import NewMessageStates
from services.address_service import get_address_owner, get_addresses_for_user
from services.auth_service import get_telegram_ids_by_user_id
from services.file_service import save_attachment_file
from services.message_service import add_attachment, create_message
from utils.telegram_helpers import extract_file_info
from utils.validators import is_valid_full_address, normalize_address

router = Router(name="new_message")

ATTACHMENT_CONTENT_TYPES = {
    ContentType.PHOTO,
    ContentType.VIDEO,
    ContentType.AUDIO,
    ContentType.VOICE,
    ContentType.DOCUMENT,
}


@router.message(F.text == "➕ پیام جدید", IsAuthenticated(), StateFilter(None))
async def start_new_message(message: Message, state: FSMContext) -> None:
    await state.set_state(NewMessageStates.recipient)
    await message.answer(
        "📮 <b>پیام جدید</b>\n\nآدرس گیرنده را وارد کنید (مثلاً <code>ali</code> یا <code>ali@pail.com</code>):",
        reply_markup=cancel_kb(),
    )


@router.message(F.text == "❌ انصراف", StateFilter(
    NewMessageStates.recipient,
    NewMessageStates.subject,
    NewMessageStates.body,
))
async def cancel_new_message_text(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer("ارسال پیام لغو شد.", reply_markup=main_menu_kb())


@router.message(NewMessageStates.recipient)
async def process_recipient(message: Message, state: FSMContext, current_user) -> None:
    raw = (message.text or "").strip()
    recipient_address = normalize_address(raw)

    if not is_valid_full_address(recipient_address):
        await message.answer("❌ آدرس نامعتبر است. دوباره وارد کنید:")
        return

    owner = await get_address_owner(recipient_address)
    if owner is None:
        await message.answer(f"❌ آدرسی به نام <code>{recipient_address}</code> وجود ندارد. دوباره وارد کنید:")
        return

    await state.update_data(recipient_address=recipient_address)

    my_addresses = await get_addresses_for_user(current_user["id"])
    address_list = [row["address"] for row in my_addresses]

    if len(address_list) == 1:
        await state.update_data(sender_address=address_list[0])
        await state.set_state(NewMessageStates.subject)
        await message.answer("📌 موضوع پیام را وارد کنید:")
        return

    await state.set_state(NewMessageStates.choose_sender)
    await message.answer(
        "📤 این پیام از کدام آدرس شما ارسال شود؟",
        reply_markup=sender_choice_kb(address_list),
    )


@router.callback_query(F.data.startswith("choose_sender_"), NewMessageStates.choose_sender)
async def process_choose_sender(callback: CallbackQuery, state: FSMContext) -> None:
    sender_address = callback.data.removeprefix("choose_sender_")
    await state.update_data(sender_address=sender_address)
    await state.set_state(NewMessageStates.subject)

    await callback.message.edit_text(f"✅ آدرس فرستنده: <code>{sender_address}</code>")
    await callback.message.answer("📌 موضوع پیام را وارد کنید:", reply_markup=cancel_kb())
    await callback.answer()


@router.message(NewMessageStates.subject)
async def process_subject(message: Message, state: FSMContext) -> None:
    subject = (message.text or "").strip()

    if not subject:
        await message.answer("❌ موضوع نمی‌تواند خالی باشد. دوباره وارد کنید:")
        return

    await state.update_data(subject=subject)
    await state.set_state(NewMessageStates.body)
    await message.answer("✍ متن پیام را بنویسید:")


@router.message(NewMessageStates.body)
async def process_body(message: Message, state: FSMContext) -> None:
    body = (message.text or "").strip()

    if not body:
        await message.answer("❌ متن پیام نمی‌تواند خالی باشد. دوباره وارد کنید:")
        return

    await state.update_data(body=body, pending_attachments=[])
    await state.set_state(NewMessageStates.attachments)
    await message.answer(
        "📎 اگر می‌خواهید فایلی (عکس، ویدیو، موزیک، ویس، سند، zip، pdf و ...) پیوست کنید ارسال کنید.\n"
        "در پایان دکمه «ارسال پیام» را بزنید:",
        reply_markup=attachment_kb(0),
    )


@router.message(NewMessageStates.attachments, F.content_type.in_(ATTACHMENT_CONTENT_TYPES))
async def process_attachment_file(message: Message, state: FSMContext) -> None:
    file_type, file_id, file_name = extract_file_info(message)

    if file_type is None:
        await message.answer("❌ نوع این فایل قابل پشتیبانی نیست.")
        return

    data = await state.get_data()
    pending_attachments = data.get("pending_attachments", [])
    pending_attachments.append({"file_type": file_type, "file_id": file_id, "file_name": file_name})
    await state.update_data(pending_attachments=pending_attachments)

    await message.answer(
        f"✅ فایل «{file_name}» اضافه شد. ({len(pending_attachments)} پیوست)",
        reply_markup=attachment_kb(len(pending_attachments)),
    )


@router.callback_query(F.data == "cancel_new_message")
async def cancel_new_message_callback(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await callback.message.edit_text("ارسال پیام لغو شد.")
    await callback.message.answer("به منوی اصلی بازگشتید:", reply_markup=main_menu_kb())
    await callback.answer()


@router.callback_query(F.data == "send_message_final", NewMessageStates.attachments)
async def finalize_new_message(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()

    sender_address = data["sender_address"]
    recipient_address = data["recipient_address"]
    subject = data["subject"]
    body = data["body"]
    pending_attachments = data.get("pending_attachments", [])

    message_id = await create_message(sender_address, recipient_address, subject, body)

    for attachment in pending_attachments:
        local_path = await save_attachment_file(
            callback.bot, attachment["file_id"], message_id, attachment["file_name"]
        )
        await add_attachment(
            message_id,
            attachment["file_type"],
            attachment["file_name"],
            attachment["file_id"],
            local_path,
        )

    await state.clear()

    await callback.message.edit_text(
        f"✅ پیام شما با موفقیت از <code>{sender_address}</code> به <code>{recipient_address}</code> ارسال شد."
    )
    await callback.message.answer("به منوی اصلی بازگشتید:", reply_markup=main_menu_kb())
    await callback.answer("پیام ارسال شد ✅")

    # اطلاع‌رسانی فوری به گیرنده (در صورت لاگین بودن)
    owner = await get_address_owner(recipient_address)
    if owner is not None:
        telegram_ids = await get_telegram_ids_by_user_id(owner["user_id"])
        for telegram_id in telegram_ids:
            try:
                await callback.bot.send_message(
                    telegram_id,
                    f"📩 پیام جدید از <code>{sender_address}</code>\n"
                    f"📌 موضوع: {subject}\n\n"
                    "برای مشاهده به «📥 صندوق ورودی» بروید.",
                )
            except Exception:
                # کاربر ممکن است ربات را مسدود کرده باشد یا در دسترس نباشد
                continue
