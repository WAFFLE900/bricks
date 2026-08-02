"""Handshake-time authentication and authorization for the collaboration socket.

Reuses the exact REST identity path: decode the HS256 JWT with
``decode_access_token`` and resolve ``sub`` (== ``user_email``) to a ``User`` the
same way ``get_current_user`` does, then gate on project permissions via
``textBox.record.project_id`` -> ``get_project_access`` (A3). Editors attach
read-write; viewers still authenticate but attach read-only (A1). Non-members and
unknown text boxes are rejected before ``websocket.accept()``.
"""

from __future__ import annotations

from dataclasses import dataclass

from fastapi import HTTPException
from starlette.concurrency import run_in_threadpool

from app.api.project_access import get_project_access
from app.collab.protocol import CLOSE_NOT_FOUND, CLOSE_UNAUTHENTICATED
from app.core.security import decode_access_token
from app.db.session import SessionLocal
from app.models.entities import TextBox, User


@dataclass(slots=True)
class CollabIdentity:
    user_id: int
    user_name: str
    user_email: str
    text_box_id: int
    project_id: int
    can_edit: bool


class CollabAuthError(Exception):
    def __init__(self, detail: str, close_code: int = CLOSE_UNAUTHENTICATED) -> None:
        super().__init__(detail)
        self.detail = detail
        self.close_code = close_code


def _resolve_identity(token: str, text_box_id: int) -> CollabIdentity:
    try:
        payload = decode_access_token(token)
    except Exception as exc:  # noqa: BLE001 - any decode failure is an auth failure
        raise CollabAuthError("Invalid access token.") from exc

    email = payload.get("sub")
    if not email:
        raise CollabAuthError("Invalid access token payload.")

    db = SessionLocal()
    try:
        user = db.query(User).filter(User.user_email == email).first()
        if user is None:
            raise CollabAuthError("User not found.")

        text_box = db.query(TextBox).filter(TextBox.id == text_box_id).first()
        if text_box is None:
            raise CollabAuthError("Text box not found.", close_code=CLOSE_NOT_FOUND)

        try:
            access = get_project_access(db, user.id, text_box.record.project_id)
        except HTTPException as exc:
            # Non-members get the same opaque 404 the REST layer returns.
            raise CollabAuthError(str(exc.detail), close_code=CLOSE_NOT_FOUND) from exc

        return CollabIdentity(
            user_id=user.id,
            user_name=user.user_name,
            user_email=user.user_email,
            text_box_id=text_box_id,
            project_id=text_box.record.project_id,
            can_edit=access.can_edit,
        )
    finally:
        db.close()


async def authenticate_ws(token: str, text_box_id: int) -> CollabIdentity:
    """Resolve and authorize a socket identity off the event loop (sync ORM)."""
    return await run_in_threadpool(_resolve_identity, token, text_box_id)
