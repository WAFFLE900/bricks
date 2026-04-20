from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class UserRead(BaseModel):
    id: int
    user_email: str
    user_name: str
    user_google_id: str | None = None
    user_facebook_id: str | None = None
    user_purpose: str | None = None
    user_identity: str | None = None
    user_otherTool: str | None = None
    user_avatar: str | None = None
    user_purpose_list: list[str] = Field(default_factory=list)
    user_other_tool_list: list[str] = Field(default_factory=list)
    has_password: bool = False
    has_google_account: bool = False
    has_facebook_account: bool = False
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SurveyUpdate(BaseModel):
    user_purpose: list[str] = Field(default_factory=list)
    user_identity: str | None = None
    user_otherTool: list[str] = Field(default_factory=list)


class UserProfileUpdate(BaseModel):
    user_name: str
    user_identity: str | None = None
    user_purpose: list[str] = Field(default_factory=list)
    user_otherTool: list[str] = Field(default_factory=list)


class PasswordChangeRequest(BaseModel):
    current_password: str | None = None
    new_password: str
