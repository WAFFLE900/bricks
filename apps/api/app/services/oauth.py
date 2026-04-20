from __future__ import annotations

from dataclasses import dataclass
from typing import Literal
from urllib.parse import urlencode

import httpx
from fastapi import HTTPException, status

from app.core.config import get_settings
from app.core.security import create_signed_token, decode_signed_token

OAuthProvider = Literal["google", "facebook"]
OAuthMode = Literal["login", "link"]


@dataclass
class OAuthProfile:
    provider: OAuthProvider
    provider_user_id: str
    email: str
    name: str
    avatar_url: str | None = None


def normalize_redirect_path(redirect: str | None, default: str = "/projects") -> str:
    if not redirect:
        return default
    if not redirect.startswith("/") or redirect.startswith("//"):
        return default
    return redirect


def build_oauth_url(
    provider: OAuthProvider,
    mode: OAuthMode,
    redirect: str | None = None,
    user_id: int | None = None,
) -> str:
    settings = get_settings()
    config = _provider_config(provider)
    redirect_path = normalize_redirect_path(redirect, default="/profile" if mode == "link" else "/projects")
    state = create_signed_token(
        {
            "provider": provider,
            "mode": mode,
            "redirect": redirect_path,
            "user_id": user_id,
        },
        expires_minutes=15,
    )

    params = {"client_id": config["client_id"], "redirect_uri": config["redirect_uri"], "state": state}
    if provider == "google":
        params.update(
            {
                "response_type": "code",
                "scope": "openid email profile",
                "access_type": "offline",
                "include_granted_scopes": "true",
                "prompt": "select_account",
            }
        )
    else:
        params.update(
            {
                "response_type": "code",
                "scope": "email,public_profile",
            }
        )

    return f"{config['authorize_url']}?{urlencode(params)}"


def parse_oauth_state(state_token: str | None) -> dict:
    if not state_token:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing OAuth state.")
    try:
        state = decode_signed_token(state_token)
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid OAuth state.") from exc

    provider = state.get("provider")
    mode = state.get("mode")
    if provider not in {"google", "facebook"} or mode not in {"login", "link"}:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid OAuth state payload.")
    return state


def build_frontend_callback_url(
    *,
    redirect: str,
    provider: OAuthProvider,
    mode: OAuthMode,
    token: str | None = None,
    error: str | None = None,
) -> str:
    settings = get_settings()
    query = {
        "redirect": normalize_redirect_path(redirect, default="/profile" if mode == "link" else "/projects"),
        "provider": provider,
        "mode": mode,
    }
    if error:
        query["error"] = error

    url = f"{settings.web_base_url.rstrip('/')}/auth/callback?{urlencode(query)}"
    if token:
        url = f"{url}#{urlencode({'access_token': token})}"
    return url


def fetch_oauth_profile(provider: OAuthProvider, code: str) -> OAuthProfile:
    config = _provider_config(provider)
    with httpx.Client(timeout=10.0) as client:
        if provider == "google":
            token_response = client.post(
                config["token_url"],
                data={
                    "code": code,
                    "client_id": config["client_id"],
                    "client_secret": config["client_secret"],
                    "redirect_uri": config["redirect_uri"],
                    "grant_type": "authorization_code",
                },
            )
            _raise_for_provider_error(token_response, provider)
            access_token = token_response.json().get("access_token")
            if not access_token:
                raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="Google did not return an access token.")

            profile_response = client.get(
                "https://openidconnect.googleapis.com/v1/userinfo",
                headers={"Authorization": f"Bearer {access_token}"},
            )
            _raise_for_provider_error(profile_response, provider)
            payload = profile_response.json()
            provider_user_id = str(payload.get("sub") or "")
            email = str(payload.get("email") or "")
            name = str(payload.get("name") or payload.get("given_name") or "")
            avatar_url = payload.get("picture")
        else:
            token_response = client.get(
                config["token_url"],
                params={
                    "client_id": config["client_id"],
                    "client_secret": config["client_secret"],
                    "redirect_uri": config["redirect_uri"],
                    "code": code,
                },
            )
            _raise_for_provider_error(token_response, provider)
            access_token = token_response.json().get("access_token")
            if not access_token:
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail="Facebook did not return an access token.",
                )

            profile_response = client.get(
                "https://graph.facebook.com/me",
                params={
                    "fields": "id,name,email,picture.type(large)",
                    "access_token": access_token,
                },
            )
            _raise_for_provider_error(profile_response, provider)
            payload = profile_response.json()
            provider_user_id = str(payload.get("id") or "")
            email = str(payload.get("email") or "")
            name = str(payload.get("name") or "")
            avatar_url = ((payload.get("picture") or {}).get("data") or {}).get("url")

    if not provider_user_id or not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{provider.title()} login did not return a usable email address.",
        )

    return OAuthProfile(
        provider=provider,
        provider_user_id=provider_user_id,
        email=email,
        name=name or email.split("@")[0],
        avatar_url=avatar_url,
    )


def _provider_config(provider: OAuthProvider) -> dict[str, str]:
    settings = get_settings()
    if provider == "google":
        values = {
            "client_id": settings.google_client_id,
            "client_secret": settings.google_client_secret,
            "redirect_uri": settings.google_redirect_uri,
            "authorize_url": "https://accounts.google.com/o/oauth2/v2/auth",
            "token_url": "https://oauth2.googleapis.com/token",
        }
    else:
        values = {
            "client_id": settings.facebook_client_id,
            "client_secret": settings.facebook_client_secret,
            "redirect_uri": settings.facebook_redirect_uri,
            "authorize_url": "https://www.facebook.com/dialog/oauth",
            "token_url": "https://graph.facebook.com/oauth/access_token",
        }

    if not values["client_id"] or not values["client_secret"] or not values["redirect_uri"]:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail=f"{provider.title()} OAuth is not configured for this environment.",
        )
    return values


def _raise_for_provider_error(response: httpx.Response, provider: OAuthProvider) -> None:
    try:
        response.raise_for_status()
    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"{provider.title()} OAuth request failed.",
        ) from exc
