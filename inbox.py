"""
هندلرهای مربوط به «صندوق ورودی»: نمایش لیست پیام‌ها، باز کردن، حذف و ستاره‌دار کردن.
"""
from aiogram import F, Router
from aiogram.filters import StateFilter
from aiogram.types import CallbackQuery, Message

from keyboards.inbox_kb import message_detail_kb, message_list_item_kb
from middlewares.auth_middleware import IsAuthenticated
from services.address_service import get_addresses_for_user
from services.message_service import (
    delete_message_for_recipient,
    get_attachments,
    get_inbox,
    get_message_by_id,
    mark_as_read,
    toggle_star,
)
from utils.formatting import format_datetime, truncate
from utils.telegram_helpers import send_attachment

router = Router(name="inbox")

BOX = "inbox"


@router.message(F.text == "📥 صندوق ورودی", IsAuthenticated(), StateFilter(None))
async def show_inbox(message: Message, current_user) -> None:
    addresses = await get_addresses_for_user(current_user["id"])
    address_list = [row["address"] for row in addresses]

    messages = await get_inbox(address_list)

    if not messages:
        await message.answer("📭 صندوق ورودی شما خالی است.")
        return

    await message.answer(f"📥 <b>صندوق ورودی</b> ({len(messages)} پیام)")

    for msg in messages:
        attachments = await get_attachments(msg["id"])
        read_icon = "✅" if msg["is_read"] else "🆕"
        attach_line = "\n📎 دارای پیوست" if attachments else ""

        text = (
            f"{read_icon} 👤 فرستنده: <code>{msg['sender_address']}</code>\n"
            f"📌 موضوع: {truncate(msg['subject'])}\n"
            f"🕒 تاریخ: {format_datetime(msg['created_at'])}"
            f"{attach_line}"
        )

        await message.answer(
            text,
            reply_markup=message_list_item_kb(msg["id"], bool(msg["is_starred"]), BOX),
        )


@router.callback_query(F.data.startswith(f"lopen_{BOX}_"))
async def open_message_from_list(callback: CallbackQuery) -> None:
    message_id = int(callback.data.removeprefix(f"lopen_{BOX}_"))
    await _open_message_detail(callback, message_id)


@router.callback_query(F.data.startswith(f"lstar_{BOX}_"))
async def toggle_star_from_list(callback: CallbackQuery) -> None:
    message_id = int(callback.data.removeprefix(f"lstar_{BOX}_"))
    is_starred = await toggle_star(message_id)

    if is_starred is None:
        await callback.answer("پیام یافت نشد.", show_alert=True)
        return

    await callback.message.edit_reply_markup(
        reply_markup=message_list_item_kb(message_id, is_starred, BOX)
    )
    await callback.answer("⭐ ستاره‌دار شد" if is_starred else "☆ ستاره برداشته شد")


@router.callback_query(F.data.startswith(f"ldelete_{BOX}_"))
async def delete_message_from_list(callback: CallbackQuery) -> None:
    message_id = int(callback.data.removeprefix(f"ldelete_{BOX}_"))
    await delete_message_for_recipient(message_id)
    await callback.message.edit_text("🗑 این پیام حذف شد.")
    await callback.answer("پیام حذف شد.")


@router.callback_query(F.data.startswith(f"dstar_{BOX}_"))
async def toggle_star_from_detail(callback: CallbackQuery) -> None:
    message_id = int(callback.data.removeprefix(f"dstar_{BOX}_"))
    is_starred = await toggle_star(message_id)

    if is_starred is None:
        await callback.answer("پیام یافت نشد.", show_alert=True)
        return

    await callback.message.edit_reply_markup(
        reply_markup=message_detail_kb(message_id, is_starred, BOX)
    )
    await callback.answer("⭐ ستاره‌دار شد" if is_starred else "☆ ستاره برداشته شد")


@router.callback_query(F.data.startswith(f"ddelete_{BOX}_"))
async def delete_message_from_detail(callback: CallbackQuery) -> None:
    message_id = int(callback.data.removeprefix(f"ddelete_{BOX}_"))
    await delete_message_for_recipient(message_id)
    await callback.message.edit_text("🗑 این پیام حذف شد.")
    await callback.answer("پیام حذف شد.")


@router.callback_query(F.data == f"dback_{BOX}")
async def back_from_detail(callback: CallbackQuery) -> None:
    await callback.message.edit_text("↩ برای دیدن لیست پیام‌ها دوباره از منو «📥 صندوق ورودی» را بزنید.")
    await callback.answer()


async def _open_message_detail(callback: CallbackQuery, message_id: int) -> None:
    msg = await get_message_by_id(message_id)

    if msg is None:
        await callback.answer("پیام یافت نشد.", show_alert=True)
        return

    if not msg["is_read"]:
        await mark_as_read(message_id)

    text = (
        f"👤 فرستنده: <code>{msg['sender_address']}</code>\n"
        f"📥 گیرنده: <code>{msg['recipient_address']}</code>\n"
        f"📌 موضوع: {msg['subject']}\n"
        f"🕒 تاریخ: {format_datetime(msg['created_at'])}\n\n"
        f"✉️ متن پیام:\n{msg['body']}"
    )

    await callback.message.answer(
        text,
        reply_markup=message_detail_kb(message_id, bool(msg["is_starred"]), BOX),
    )

    attachments = await get_attachments(message_id)
    for attachment in attachments:
        await send_attachment(callback.bot, callback.from_user.id, attachment)

    await callback.answer()
