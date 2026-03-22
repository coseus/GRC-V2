from __future__ import annotations

from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def _validate_bcrypt_password_length(password: str) -> None:
    if password is None:
        raise ValueError("Parola lipseste.")

    if len(password.encode("utf-8")) > 72:
        raise ValueError("Parola este prea lunga pentru bcrypt. Foloseste maxim 72 bytes.")


def hash_password(password: str) -> str:
    _validate_bcrypt_password_length(password)
    return pwd_context.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    _validate_bcrypt_password_length(password)
    return pwd_context.verify(password, password_hash)


def validate_password_strength(password: str) -> None:
    password = (password or "").strip()

    if len(password) < 8:
        raise ValueError("Parola trebuie sa aiba minim 8 caractere.")

    if len(password.encode("utf-8")) > 72:
        raise ValueError("Parola trebuie sa aiba maxim 72 bytes pentru bcrypt.")

    if password.lower() in {"password", "admin123", "12345678", "qwerty123"}:
        raise ValueError("Parola este prea slaba.")