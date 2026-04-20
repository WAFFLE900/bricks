from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict


class TextBoxCreate(BaseModel):
    textBox_content: str


class TextBoxUpdate(TextBoxCreate):
    pass


class TextBoxRead(BaseModel):
    id: int
    textBox_content: str | None
    updated_at: datetime | None = None
    tags: list[str] = []

    model_config = ConfigDict(from_attributes=True)


class RecordCreate(BaseModel):
    record_name: str
    record_date: date | None = None
    record_department: str | None = None
    record_attendances: int | None = None
    record_place: str | None = None
    record_host_name: str | None = None


class RecordUpdate(BaseModel):
    record_name: str | None = None
    record_date: date | None = None
    record_department: str | None = None
    record_attendances: int | None = None
    record_place: str | None = None
    record_host_name: str | None = None


class RecordRead(BaseModel):
    id: int
    record_name: str
    record_date: date | None
    record_department: str | None
    record_attendances: int | None
    record_place: str | None
    record_host_name: str | None
    record_trashcan: bool
    created_at: datetime
    updated_at: datetime
    tags: list[str] = []
    text_boxes: list[TextBoxRead] = []

    model_config = ConfigDict(from_attributes=True)


class RecordTrashUpdate(BaseModel):
    in_trash: bool

