from __future__ import annotations

import hashlib
from datetime import datetime, timedelta, timezone

import jwt

from app.core.config import get_settings


ALGORITHM = "HS256"


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def verify_password(plain_password: str, hashed_password: str | None) -> bool:
    if hashed_password is None:
        return False
    return hash_password(plain_password) == hashed_password


def create_access_token(subject: str) -> str:
    return create_signed_token({"sub": subject}, expires_minutes=get_settings().access_token_expire_minutes)


def create_signed_token(payload: dict, expires_minutes: int = 15) -> str:
    settings = get_settings()
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=expires_minutes)
    return jwt.encode({**payload, "exp": expires_at}, settings.secret_key, algorithm=ALGORITHM)


def decode_access_token(token: str) -> dict:
    return decode_signed_token(token)


def decode_signed_token(token: str) -> dict:
    settings = get_settings()
    return jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])
