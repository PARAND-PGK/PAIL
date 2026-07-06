"""
توابع اعتبارسنجی ورودی‌های کاربر (نام کاربری، رمز عبور، آدرس PAIL).
"""
import re

from config.settings import ADDRESS_DOMAIN

USERNAME_PATTERN = re.compile(r"^[a-zA-Z0-9_]{3,32}$")
ADDRESS_LOCAL_PATTERN = re.compile(r"^[a-zA-Z0-9_.]{2,32}$")

MIN_PASSWORD_LENGTH = 6


def is_valid_username(username: str) -> bool:
    """نام کاربری باید فقط شامل حروف انگلیسی، عدد و آندرلاین و بین ۳ تا ۳۲ کاراکتر باشد."""
    return bool(username) and bool(USERNAME_PATTERN.match(username))


def is_valid_password(password: str) -> bool:
    """رمز عبور باید حداقل ۶ کاراکتر باشد."""
    return isinstance(password, str) and len(password) >= MIN_PASSWORD_LENGTH


def is_valid_address_local_part(local_part: str) -> bool:
    """قسمت قبل از @ در آدرس باید فقط حروف انگلیسی، عدد، نقطه و آندرلاین باشد."""
    return bool(local_part) and bool(ADDRESS_LOCAL_PATTERN.match(local_part))


def normalize_address(raw: str) -> str:
    """
    ورودی کاربر را به یک آدرس کامل PAIL تبدیل می‌کند.
    اگر کاربر فقط 'ali' وارد کند، خروجی 'ali@pail.com' خواهد بود.
    """
    raw = (raw or "").strip().lower()
    if "@" in raw:
        return raw
    return f"{raw}{ADDRESS_DOMAIN}"


def extract_local_part(address: str) -> str:
    """قسمت قبل از @ را از یک آدرس کامل استخراج می‌کند."""
    return address.split("@")[0] if "@" in address else address


def is_valid_full_address(address: str) -> bool:
    """بررسی می‌کند آدرس کامل، معتبر و متعلق به دامنه pail.com باشد."""
    if not address.endswith(ADDRESS_DOMAIN):
        return False
    local_part = extract_local_part(address)
    return is_valid_address_local_part(local_part)
