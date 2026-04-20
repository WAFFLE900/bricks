from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.security import hash_password, verify_password
from app.db.session import get_db
from app.models.entities import SearchHistory, User
from app.schemas.auth import OAuthUrlResponse
from app.schemas.user import PasswordChangeRequest, UserProfileUpdate, UserRead
from app.services.oauth import build_oauth_url

router = APIRouter()


@router.get("/me/search-history")
def get_search_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    items = (
        db.query(SearchHistory)
        .filter(SearchHistory.user_id == current_user.id)
        .order_by(SearchHistory.search_time.desc())
        .limit(10)
        .all()
    )
    return {"items": [item.search_content for item in items]}


@router.patch("/me", response_model=UserRead)
def update_profile(
    payload: UserProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> UserRead:
    user_name = payload.user_name.strip()
    if not user_name:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Display name cannot be empty.")

    current_user.user_name = user_name
    current_user.user_identity = payload.user_identity.strip() if payload.user_identity else None
    current_user.user_purpose = ",".join(payload.user_purpose) if payload.user_purpose else None
    current_user.user_otherTool = ",".join(payload.user_otherTool) if payload.user_otherTool else None
    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    return UserRead.model_validate(current_user)


@router.post("/me/password", response_model=UserRead)
def change_password(
    payload: PasswordChangeRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> UserRead:
    new_password = payload.new_password.strip()
    if len(new_password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 8 characters long.",
        )

    if current_user.user_password:
        if not payload.current_password or not verify_password(payload.current_password, current_user.user_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect.",
            )

        if verify_password(new_password, current_user.user_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="New password must be different from the current password.",
            )

    current_user.user_password = hash_password(new_password)
    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    return UserRead.model_validate(current_user)


@router.get("/me/social-accounts/{provider}/link-url", response_model=OAuthUrlResponse)
def get_social_link_url(
    provider: str,
    redirect: str | None = None,
    current_user: User = Depends(get_current_user),
) -> OAuthUrlResponse:
    if provider not in {"google", "facebook"}:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Unsupported OAuth provider.")

    return OAuthUrlResponse(
        auth_url=build_oauth_url(
            provider,
            mode="link",
            redirect=redirect,
            user_id=current_user.id,
        )
    )
