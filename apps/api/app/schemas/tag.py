from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class TagCreate(BaseModel):
    tag_name: str
    tag_class: str | None = None


class TagRead(BaseModel):
    id: int
    tag_name: str
    tag_class: str | None = None

    model_config = ConfigDict(from_attributes=True)


class TagAttach(BaseModel):
    tag_id: int

