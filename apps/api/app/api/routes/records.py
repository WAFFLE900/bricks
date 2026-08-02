from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session, selectinload

from app.api.deps import get_current_user
from app.api.project_access import get_project_access, require_project_editor
from app.db.session import get_db
from app.models.entities import Record, TextBox, User
from app.schemas.record import RecordCreate, RecordRead, RecordTrashUpdate, RecordUpdate, TextBoxCreate, TextBoxRead, TextBoxUpdate
from app.services.mentions import notify_new_mentions

router = APIRouter()


def _record_or_404(db: Session, record_id: int) -> Record:
    record = (
        db.query(Record)
        .filter(Record.id == record_id)
        .options(selectinload(Record.text_boxes).selectinload(TextBox.tags))
        .first()
    )
    if record is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Record not found.")
    return record


def _serialize_record(record: Record) -> RecordRead:
    tags = sorted({tag.tag_name for text_box in record.text_boxes for tag in text_box.tags})
    text_boxes = [
        TextBoxRead(
            id=text_box.id,
            textBox_content=text_box.textBox_content,
            updated_at=text_box.updated_at,
            tags=[tag.tag_name for tag in text_box.tags],
        )
        for text_box in record.text_boxes
    ]
    return RecordRead(
        id=record.id,
        record_name=record.record_name,
        record_date=record.record_date,
        record_department=record.record_department,
        record_attendances=record.record_attendances,
        record_place=record.record_place,
        record_host_name=record.record_host_name,
        record_trashcan=record.record_trashcan,
        created_at=record.created_at,
        updated_at=record.updated_at,
        tags=tags,
        text_boxes=text_boxes,
    )


@router.get("/projects/{project_id}/records", response_model=list[RecordRead])
def list_records(
    project_id: int,
    include_trashed: bool = Query(default=False),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[RecordRead]:
    get_project_access(db, current_user.id, project_id)
    query = (
        db.query(Record)
        .filter(Record.project_id == project_id)
        .options(selectinload(Record.text_boxes).selectinload(TextBox.tags))
        .order_by(Record.updated_at.desc())
    )
    if not include_trashed:
        query = query.filter(Record.record_trashcan.is_(False))
    return [_serialize_record(record) for record in query.all()]


@router.post("/projects/{project_id}/records", response_model=RecordRead, status_code=status.HTTP_201_CREATED)
def create_record(
    project_id: int,
    payload: RecordCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> RecordRead:
    access = get_project_access(db, current_user.id, project_id)
    require_project_editor(access)

    record = Record(project_id=project_id, user_id=current_user.id, **payload.model_dump())
    db.add(record)
    db.commit()
    db.refresh(record)
    return _serialize_record(record)


@router.get("/projects/{project_id}/records/{record_id}", response_model=RecordRead)
def get_record(
    project_id: int,
    record_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> RecordRead:
    get_project_access(db, current_user.id, project_id)
    record = _record_or_404(db, record_id)
    if record.project_id != project_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Record not found in project.")
    return _serialize_record(record)


@router.patch("/records/{record_id}", response_model=RecordRead)
def update_record(
    record_id: int,
    payload: RecordUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> RecordRead:
    record = _record_or_404(db, record_id)
    access = get_project_access(db, current_user.id, record.project_id)
    require_project_editor(access)

    for key, value in payload.model_dump(exclude_none=True).items():
        setattr(record, key, value)
    db.add(record)
    db.commit()
    db.refresh(record)
    return _serialize_record(record)


@router.patch("/records/{record_id}/trash", response_model=RecordRead)
def update_record_trash(
    record_id: int,
    payload: RecordTrashUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> RecordRead:
    record = _record_or_404(db, record_id)
    access = get_project_access(db, current_user.id, record.project_id)
    require_project_editor(access)

    record.record_trashcan = payload.in_trash
    db.add(record)
    db.commit()
    db.refresh(record)
    return _serialize_record(record)


@router.delete("/records/{record_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_record(
    record_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Response:
    record = _record_or_404(db, record_id)
    access = get_project_access(db, current_user.id, record.project_id)
    require_project_editor(access)

    db.delete(record)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/records/{record_id}/text-boxes", response_model=TextBoxRead, status_code=status.HTTP_201_CREATED)
def create_text_box(
    record_id: int,
    payload: TextBoxCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> TextBoxRead:
    record = _record_or_404(db, record_id)
    access = get_project_access(db, current_user.id, record.project_id)
    require_project_editor(access)

    text_box = TextBox(record_id=record_id, **payload.model_dump())
    db.add(text_box)
    db.flush()
    notify_new_mentions(
        db,
        actor=current_user,
        project=access.project,
        record=record,
        content=text_box.textBox_content,
    )
    db.commit()
    db.refresh(text_box)
    return TextBoxRead(id=text_box.id, textBox_content=text_box.textBox_content, updated_at=text_box.updated_at, tags=[])


@router.patch("/text-boxes/{text_box_id}", response_model=TextBoxRead)
def update_text_box(
    text_box_id: int,
    payload: TextBoxUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> TextBoxRead:
    text_box = (
        db.query(TextBox)
        .options(selectinload(TextBox.tags), selectinload(TextBox.record))
        .filter(TextBox.id == text_box_id)
        .first()
    )
    if text_box is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Text box not found.")

    access = get_project_access(db, current_user.id, text_box.record.project_id)
    require_project_editor(access)

    previous_content = text_box.textBox_content
    text_box.textBox_content = payload.textBox_content
    db.add(text_box)
    db.flush()
    notify_new_mentions(
        db,
        actor=current_user,
        project=access.project,
        record=text_box.record,
        content=text_box.textBox_content,
        previous_content=previous_content,
    )
    db.commit()
    db.refresh(text_box)
    return TextBoxRead(
        id=text_box.id,
        textBox_content=text_box.textBox_content,
        updated_at=text_box.updated_at,
        tags=[tag.tag_name for tag in text_box.tags],
    )
