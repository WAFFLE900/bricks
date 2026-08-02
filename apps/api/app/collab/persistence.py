"""Postgres materialization for collaboration rooms.

Runs on its own threadpool session (never the request-scoped ``get_db`` generator),
writing back through the ORM so ``TextBox.updated_at`` ``onupdate`` fires and REST
reads/search/tags keep working unchanged (A4/F5). The mention/notification diff that
lives in the REST PATCH path is re-hooked here via ``app.services.mentions`` so
mentions still fire when content settles from a collaborative edit.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

from sqlalchemy.orm import selectinload
from starlette.concurrency import run_in_threadpool

from app.api.project_access import project_load_options
from app.db.session import SessionLocal
from app.models.entities import Project, TextBox, User
from app.services.mentions import notify_new_mentions

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class TextBoxSnapshot:
    state: bytes | None
    text: str | None


def _load_snapshot(text_box_id: int) -> TextBoxSnapshot | None:
    db = SessionLocal()
    try:
        text_box = db.query(TextBox).filter(TextBox.id == text_box_id).first()
        if text_box is None:
            return None
        return TextBoxSnapshot(state=text_box.textBox_crdt_state, text=text_box.textBox_content)
    finally:
        db.close()


async def load_snapshot(text_box_id: int) -> TextBoxSnapshot | None:
    return await run_in_threadpool(_load_snapshot, text_box_id)


def _persist(text_box_id: int, state: bytes | None, text: str | None, actor_user_id: int) -> None:
    db = SessionLocal()
    try:
        text_box = (
            db.query(TextBox)
            .options(selectinload(TextBox.record))
            .filter(TextBox.id == text_box_id)
            .first()
        )
        if text_box is None:
            return

        previous_content = text_box.textBox_content
        if text is not None:
            text_box.textBox_content = text
        if state is not None:
            text_box.textBox_crdt_state = state
        db.add(text_box)
        db.flush()

        record = text_box.record
        actor = db.query(User).filter(User.id == actor_user_id).first()
        project = (
            db.query(Project)
            .options(*project_load_options())
            .filter(Project.id == record.project_id)
            .first()
        )
        if text is not None and actor is not None and project is not None:
            notify_new_mentions(
                db,
                actor=actor,
                project=project,
                record=record,
                content=text_box.textBox_content,
                previous_content=previous_content,
            )
        db.commit()
    finally:
        db.close()


async def persist_snapshot(text_box_id: int, state: bytes | None, text: str | None, actor_user_id: int) -> None:
    await run_in_threadpool(_persist, text_box_id, state, text, actor_user_id)
