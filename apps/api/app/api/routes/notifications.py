from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session, selectinload

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.entities import Notification, User
from app.schemas.notification import NotificationRead

router = APIRouter()


def _serialize_notification(notification: Notification) -> NotificationRead:
    return NotificationRead(
        id=notification.id,
        notification_type=notification.notification_type,
        notification_title=notification.notification_title,
        notification_body=notification.notification_body,
        is_read=notification.is_read,
        created_at=notification.created_at,
        project_id=notification.project.id,
        project_name=notification.project.project_name,
        actor_name=notification.actor.user_name,
    )


@router.get("/notifications", response_model=list[NotificationRead])
def list_notifications(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[NotificationRead]:
    items = (
        db.query(Notification)
        .filter(Notification.recipient_user_id == current_user.id)
        .options(selectinload(Notification.project), selectinload(Notification.actor))
        .order_by(Notification.created_at.desc(), Notification.id.desc())
        .limit(20)
        .all()
    )
    return [_serialize_notification(item) for item in items]


@router.post("/notifications/{notification_id}/read", response_model=NotificationRead)
def mark_notification_read(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> NotificationRead:
    notification = (
        db.query(Notification)
        .filter(Notification.id == notification_id, Notification.recipient_user_id == current_user.id)
        .options(selectinload(Notification.project), selectinload(Notification.actor))
        .first()
    )
    if notification is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found.")

    notification.is_read = True
    db.add(notification)
    db.commit()
    db.refresh(notification)
    return _serialize_notification(notification)


@router.post("/notifications/read-all", status_code=status.HTTP_204_NO_CONTENT)
def mark_all_notifications_read(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Response:
    (
        db.query(Notification)
        .filter(Notification.recipient_user_id == current_user.id, Notification.is_read.is_(False))
        .update({"is_read": True})
    )
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
