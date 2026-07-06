"""
میان‌افزار احراز هویت: قبل از رسیدن هر پیام/کالبک به هندلرها،
کاربر لاگین‌شده متصل به chat_id فعلی تلگرام را در دیتا قرار می‌دهد (current_user).

همچنین دو فیلتر ساده IsAuthenticated و IsGuest برای استفاده در هندلرها.
"""
from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.filters import BaseFilter
from aiogram.types import TelegramObject

from services.auth_service import get_logged_in_user


class AuthMiddleware(BaseMiddleware):
    """کاربر جاری (در صورت لاگین بودن) را در data['current_user'] قرار می‌دهد."""

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        current_user = None
        telegram_user = getattr(event, "from_user", None)

        if telegram_user is not None:
            current_user = await get_logged_in_user(telegram_user.id)

        data["current_user"] = current_user
        return await handler(event, data)


class IsAuthenticated(BaseFilter):
    """فقط زمانی True است که کاربر وارد حساب کاربری خود شده باشد."""

    async def __call__(self, event: TelegramObject, current_user) -> bool:
        return current_user is not None


class IsGuest(BaseFilter):
    """فقط زمانی True است که کاربر هنوز وارد حساب کاربری نشده باشد."""

    async def __call__(self, event: TelegramObject, current_user) -> bool:
        return current_user is None
