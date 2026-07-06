"""
هندلر مربوط به نمایش پروفایل کاربر: نام کاربری، عکس پروفایل تلگرام، بیوگرافی و آدرس‌های PAIL.
"""
from aiogram import F, Router
from aiogram.filters import StateFilter
from aiogram.types import Message

from middlewares.auth_middleware import IsAuthenticated
from services.address_service import get_addresses_for_user

router = Router(name="profile")


@router.message(F.text == "👤 پروفایل", IsAuthenticated(), StateFilter(None))
async def show_profile(message: Message, current_user) -> None:
    addresses = await get_addresses_for_user(current_user["id"])

    if addresses:
        address_lines = "\n".join(f"• <code>{row['address']}</code>" for row in addresses)
    else:
        address_lines = "هنوز آدرسی نساخته‌اید."

    bio = current_user["bio"] or "بدون بیوگرافی"

    caption = (
        f"👤 <b>پروفایل کاربری</b>\n\n"
        f"نام کاربری: <b>{current_user['username']}</b>\n"
        f"بیوگرافی: {bio}\n\n"
        f"📮 آدرس‌های PAIL شما:\n{address_lines}"
    )

    photos = await message.bot.get_user_profile_photos(message.from_user.id, limit=1)

    if photos.total_count > 0:
        file_id = photos.photos[0][-1].file_id
        await message.answer_photo(file_id, caption=caption)
    else:
        await message.answer(caption)
