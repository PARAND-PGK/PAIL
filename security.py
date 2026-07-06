"""
توابع مربوط به امنیت: هش کردن و بررسی رمز عبور.
از pbkdf2_hmac استاندارد کتابخانه hashlib استفاده می‌شود (بدون نیاز به وابستگی خارجی).
"""
import hashlib
import hmac
import os

_ITERATIONS = 100_000
_ALGORITHM = "sha256"


def hash_password(password: str) -> str:
    """رمز عبور را با یک salt تصادفی هش می‌کند و رشته 'salt:hash' را برمی‌گرداند."""
    salt = os.urandom(16)
    pwd_hash = hashlib.pbkdf2_hmac(_ALGORITHM, password.encode("utf-8"), salt, _ITERATIONS)
    return f"{salt.hex()}:{pwd_hash.hex()}"


def verify_password(password: str, stored_hash: str) -> bool:
    """رمز عبور وارد شده را با هش ذخیره‌شده مقایسه می‌کند."""
    try:
        salt_hex, hash_hex = stored_hash.split(":")
        salt = bytes.fromhex(salt_hex)
        expected = bytes.fromhex(hash_hex)
    except (ValueError, AttributeError):
        return False

    pwd_hash = hashlib.pbkdf2_hmac(_ALGORITHM, password.encode("utf-8"), salt, _ITERATIONS)
    return hmac.compare_digest(pwd_hash, expected)
