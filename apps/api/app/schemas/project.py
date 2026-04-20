from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


ProjectStatus = Literal["active", "ended", "trash", "all"]
ProjectState = Literal["open", "end"]
ProjectMemberPermission = Literal["view", "edit"]
ProjectUserPermission = Literal["owner", "view", "edit"]


class ProjectCreate(BaseModel):
    project_name: str
    project_type: str | None = None
    project_image: str | None = None
    project_edit: bool = True
    project_visible: bool = True
    project_comment: bool = True


class ProjectMemberRead(BaseModel):
    user_id: int
    user_name: str
    user_email: str
    role: Literal["owner", "member"]
    permission: ProjectMemberPermission
    can_edit: bool
    joined_at: datetime


class ProjectRead(BaseModel):
    id: int
    project_type: str | None
    project_image: str | None
    project_name: str
    project_trashcan: bool
    project_ended: bool
    project_edit: bool
    project_visible: bool
    project_comment: bool
    project_creation_date: datetime
    project_edit_date: datetime
    owner_name: str
    owner_email: str
    current_user_permission: ProjectUserPermission
    can_edit_content: bool
    can_manage_members: bool
    member_count: int
    members: list[ProjectMemberRead] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class ProjectStateUpdate(BaseModel):
    state: ProjectState


class ProjectTrashUpdate(BaseModel):
    in_trash: bool


class ProjectTypeRename(BaseModel):
    old_project_type: str
    project_type: str


class ProjectMemberInvite(BaseModel):
    user_email: str
    permission: ProjectMemberPermission = "view"


class ProjectMemberPermissionUpdate(BaseModel):
    permission: ProjectMemberPermission
