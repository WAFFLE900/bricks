from __future__ import annotations

from pydantic import BaseModel

from app.schemas.user import UserRead


class LoginRequest(BaseModel):
    user_email: str
    user_password: str


class RegisterRequest(LoginRequest):
    user_name: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserRead


class OAuthUrlResponse(BaseModel):
    auth_url: str
