from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel


NotificationType = Literal["project_invite", "project_permission_updated", "text_box_mention"]


class NotificationRead(BaseModel):
    id: int
    notification_type: NotificationType
    notification_title: str
    notification_body: str
    is_read: bool
    created_at: datetime
    project_id: int
    project_name: str
    actor_name: str
