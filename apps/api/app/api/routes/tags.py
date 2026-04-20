from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session, selectinload

from app.api.deps import get_current_user
from app.api.project_access import get_project_access, require_project_editor
from app.db.session import get_db
from app.models.entities import Tag, TextBox, User
from app.schemas.tag import TagAttach, TagCreate, TagRead

router = APIRouter()


@router.get("/tags", response_model=list[TagRead])
def list_tags(
    query: str | None = Query(default=None),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
) -> list[TagRead]:
    tag_query = db.query(Tag)
    if query:
        tag_query = tag_query.filter(Tag.tag_name.ilike(f"%{query}%"))
    tags = tag_query.order_by(Tag.tag_name.asc()).all()
    return [TagRead.model_validate(tag) for tag in tags]


@router.post("/tags", response_model=TagRead, status_code=status.HTTP_201_CREATED)
def create_tag(
    payload: TagCreate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
) -> TagRead:
    existing = db.query(Tag).filter(Tag.tag_name == payload.tag_name).first()
    if existing is not None:
        return TagRead.model_validate(existing)
    tag = Tag(**payload.model_dump())
    db.add(tag)
    db.commit()
    db.refresh(tag)
    return TagRead.model_validate(tag)


def _text_box_or_404(db: Session, text_box_id: int) -> TextBox:
    text_box = (
        db.query(TextBox)
        .options(selectinload(TextBox.tags), selectinload(TextBox.record))
        .filter(TextBox.id == text_box_id)
        .first()
    )
    if text_box is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Text box not found.")
    return text_box


@router.post("/text-boxes/{text_box_id}/tags", response_model=TagRead)
def attach_tag(
    text_box_id: int,
    payload: TagAttach,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> TagRead:
    text_box = _text_box_or_404(db, text_box_id)
    access = get_project_access(db, current_user.id, text_box.record.project_id)
    require_project_editor(access)

    tag = db.query(Tag).filter(Tag.id == payload.tag_id).first()
    if tag is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tag not found.")

    if tag not in text_box.tags:
        text_box.tags.append(tag)
        db.add(text_box)
        db.commit()
    return TagRead.model_validate(tag)


@router.delete("/text-boxes/{text_box_id}/tags/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
def detach_tag(
    text_box_id: int,
    tag_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Response:
    text_box = _text_box_or_404(db, text_box_id)
    access = get_project_access(db, current_user.id, text_box.record.project_id)
    require_project_editor(access)

    text_box.tags = [tag for tag in text_box.tags if tag.id != tag_id]
    db.add(text_box)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
