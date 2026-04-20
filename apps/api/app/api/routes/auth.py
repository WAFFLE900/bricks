from __future__ import annotations

from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.security import create_access_token, hash_password, verify_password
from app.db.session import get_db
from app.models.entities import User
from app.schemas.auth import LoginRequest, OAuthUrlResponse, RegisterRequest, TokenResponse
from app.schemas.user import SurveyUpdate, UserRead
from app.services.oauth import (
    OAuthProfile,
    build_frontend_callback_url,
    build_oauth_url,
    fetch_oauth_profile,
    normalize_redirect_path,
    parse_oauth_state,
)

router = APIRouter()


def _token_response(user: User) -> TokenResponse:
    return TokenResponse(access_token=create_access_token(user.user_email), user=UserRead.model_validate(user))


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, db: Session = Depends(get_db)) -> TokenResponse:
    existing = db.query(User).filter(User.user_email == payload.user_email).first()
    if existing is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered.")

    user = User(
        user_email=payload.user_email,
        user_password=hash_password(payload.user_password),
        user_name=payload.user_name,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return _token_response(user)


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    user = db.query(User).filter(User.user_email == payload.user_email).first()
    if user is None or not verify_password(payload.user_password, user.user_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password.")
    return _token_response(user)


@router.get("/me", response_model=UserRead)
def me(current_user: User = Depends(get_current_user)) -> UserRead:
    return UserRead.model_validate(current_user)


@router.post("/survey", response_model=UserRead)
def complete_survey(
    payload: SurveyUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> UserRead:
    current_user.user_purpose = ",".join(payload.user_purpose) if payload.user_purpose else None
    current_user.user_identity = payload.user_identity
    current_user.user_otherTool = ",".join(payload.user_otherTool) if payload.user_otherTool else None
    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    return UserRead.model_validate(current_user)


@router.get("/google/url", response_model=OAuthUrlResponse)
def google_auth_url(redirect: str | None = None) -> OAuthUrlResponse:
    return OAuthUrlResponse(auth_url=build_oauth_url("google", mode="login", redirect=redirect))


@router.get("/facebook/url", response_model=OAuthUrlResponse)
def facebook_auth_url(redirect: str | None = None) -> OAuthUrlResponse:
    return OAuthUrlResponse(auth_url=build_oauth_url("facebook", mode="login", redirect=redirect))


@router.get("/google/callback")
def google_callback(
    code: str | None = None,
    state: str | None = None,
    error: str | None = None,
    error_description: str | None = None,
    db: Session = Depends(get_db),
) -> RedirectResponse:
    return _oauth_callback(
        provider="google",
        code=code,
        state_token=state,
        error=error,
        error_description=error_description,
        db=db,
    )


@router.get("/facebook/callback")
def facebook_callback(
    code: str | None = None,
    state: str | None = None,
    error: str | None = None,
    error_description: str | None = None,
    db: Session = Depends(get_db),
) -> RedirectResponse:
    return _oauth_callback(
        provider="facebook",
        code=code,
        state_token=state,
        error=error,
        error_description=error_description,
        db=db,
    )


def _oauth_callback(
    *,
    provider: Literal["google", "facebook"],
    code: str | None,
    state_token: str | None,
    error: str | None,
    error_description: str | None,
    db: Session,
) -> RedirectResponse:
    try:
        state = parse_oauth_state(state_token)
        redirect_path = normalize_redirect_path(state.get("redirect"), default="/profile" if state["mode"] == "link" else "/projects")
        mode = state["mode"]
    except HTTPException as exc:
        return RedirectResponse(
            build_frontend_callback_url(
                redirect="/login",
                provider=provider,
                mode="login",
                error=exc.detail,
            )
        )

    if error:
        message = error_description or error
        return RedirectResponse(
            build_frontend_callback_url(
                redirect=redirect_path,
                provider=provider,
                mode=mode,
                error=message,
            )
        )

    if not code:
        return RedirectResponse(
            build_frontend_callback_url(
                redirect=redirect_path,
                provider=provider,
                mode=mode,
                error="Missing OAuth authorization code.",
            )
        )

    try:
        profile = fetch_oauth_profile(provider, code)
        user = _resolve_oauth_user(
            profile=profile,
            mode=mode,
            link_user_id=state.get("user_id"),
            db=db,
        )
        return RedirectResponse(
            build_frontend_callback_url(
                redirect=redirect_path,
                provider=provider,
                mode=mode,
                token=create_access_token(user.user_email),
            )
        )
    except HTTPException as exc:
        return RedirectResponse(
            build_frontend_callback_url(
                redirect=redirect_path,
                provider=provider,
                mode=mode,
                error=exc.detail,
            )
        )


def _resolve_oauth_user(profile: OAuthProfile, mode: str, link_user_id: int | None, db: Session) -> User:
    provider_field = "user_google_id" if profile.provider == "google" else "user_facebook_id"
    provider_owner = db.query(User).filter(getattr(User, provider_field) == profile.provider_user_id).first()

    if mode == "link":
        if not link_user_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing user binding context.")

        current_user = db.query(User).filter(User.id == link_user_id).first()
        if current_user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found.")

        if provider_owner and provider_owner.id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"This {profile.provider.title()} account is already linked to another BRICKS account.",
            )

        email_owner = db.query(User).filter(User.user_email == profile.email).first()
        if email_owner and email_owner.id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="This email address is already used by another BRICKS account.",
            )

        setattr(current_user, provider_field, profile.provider_user_id)
        if not current_user.user_avatar and profile.avatar_url:
            current_user.user_avatar = profile.avatar_url
        if not current_user.user_name.strip():
            current_user.user_name = profile.name
        db.add(current_user)
        db.commit()
        db.refresh(current_user)
        return current_user

    if provider_owner:
        if not provider_owner.user_avatar and profile.avatar_url:
            provider_owner.user_avatar = profile.avatar_url
            db.add(provider_owner)
            db.commit()
            db.refresh(provider_owner)
        return provider_owner

    user = db.query(User).filter(User.user_email == profile.email).first()
    if user is None:
        user = User(
            user_email=profile.email,
            user_name=profile.name,
            user_avatar=profile.avatar_url,
        )

    setattr(user, provider_field, profile.provider_user_id)
    if not user.user_avatar and profile.avatar_url:
        user.user_avatar = profile.avatar_url
    if not user.user_name.strip():
        user.user_name = profile.name
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
