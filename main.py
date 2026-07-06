"""
نقطه ورود اصلی پروژه PAIL.
یک سامانه پیام‌رسانی خصوصی شبیه به ایمیل که فقط درون تلگرام کار می‌کند.

اجرا:
    python main.py
"""
import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from config.settings import BOT_TOKEN
from database.db import init_db
from middlewares.auth_middleware import AuthMiddleware

from handlers import (
    inbox,
    login,
    menu,
    new_message,
    profile,
    register,
    sent,
    settings as settings_handlers,
    start,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("PAIL")


async def main() -> None:
    if not BOT_TOKEN:
        raise RuntimeError(
            "BOT_TOKEN تنظیم نشده است. لطفاً فایل .env را بر اساس .env.example بسازید و توکن ربات را وارد کنید."
        )

    logger.info("در حال آماده‌سازی دیتابیس...")
    await init_db()

    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher(storage=MemoryStorage())

    # میان‌افزار احراز هویت برای پیام‌ها و کالبک‌ها
    # نکته: باید outer_middleware باشد تا قبل از چک شدن فیلترهایی مثل
    # IsGuest/IsAuthenticated اجرا شود و current_user در data موجود باشد.
    dp.message.outer_middleware(AuthMiddleware())
    dp.callback_query.outer_middleware(AuthMiddleware())

    # ترتیب ثبت روترها مهم است؛ روتر عمومی «menu» باید همیشه آخرین مورد باشد.
    dp.include_router(start.router)
    dp.include_router(register.router)
    dp.include_router(login.router)
    dp.include_router(new_message.router)
    dp.include_router(inbox.router)
    dp.include_router(sent.router)
    dp.include_router(profile.router)
    dp.include_router(settings_handlers.router)
    dp.include_router(menu.router)

    await bot.delete_webhook(drop_pending_updates=True)

    logger.info("ربات PAIL در حال اجراست...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("ربات متوقف شد.")
