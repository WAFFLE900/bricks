from __future__ import annotations

from difflib import SequenceMatcher

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.api.project_access import accessible_projects_query, project_load_options
from app.db.session import get_db
from app.models.entities import SearchHistory, User
from app.schemas.project import ProjectRead, ProjectStatus

router = APIRouter()


def _serialize_project(project, current_user_id: int) -> dict:
    membership = next((item for item in project.memberships if item.user_id == current_user_id), None)
    current_user_permission = "owner" if project.user_id == current_user_id else membership.permission

    members = [
        {
            "user_id": project.user.id,
            "user_name": project.user.user_name,
            "user_email": project.user.user_email,
            "role": "owner",
            "permission": "edit",
            "can_edit": True,
            "joined_at": project.project_creation_date,
        }
    ]
    members.extend(
        {
            "user_id": item.user.id,
            "user_name": item.user.user_name,
            "user_email": item.user.user_email,
            "role": "member",
            "permission": item.permission,
            "can_edit": item.permission == "edit",
            "joined_at": item.created_at,
        }
        for item in project.memberships
    )

    return ProjectRead(
        id=project.id,
        project_type=project.project_type,
        project_image=project.project_image,
        project_name=project.project_name,
        project_trashcan=project.project_trashcan,
        project_ended=project.project_ended,
        project_edit=project.project_edit,
        project_visible=project.project_visible,
        project_comment=project.project_comment,
        project_creation_date=project.project_creation_date,
        project_edit_date=project.project_edit_date,
        owner_name=project.user.user_name,
        owner_email=project.user.user_email,
        current_user_permission=current_user_permission,
        can_edit_content=current_user_permission in {"owner", "edit"},
        can_manage_members=current_user_permission == "owner",
        member_count=len(members),
        members=members,
    ).model_dump()


@router.get("/projects")
def search_projects(
    q: str = Query(..., min_length=1),
    status_name: ProjectStatus = Query(default="all", alias="status"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = accessible_projects_query(db, current_user.id).options(*project_load_options())
    if status_name == "active":
        query = query.filter_by(project_trashcan=False, project_ended=False)
    elif status_name == "ended":
        query = query.filter_by(project_trashcan=False, project_ended=True)
    elif status_name == "trash":
        query = query.filter_by(project_trashcan=True)

    items = []
    for project in query.all():
        score = SequenceMatcher(None, q.lower(), project.project_name.lower()).ratio()
        item = _serialize_project(project, current_user.id)
        item["score"] = round(score, 4)
        items.append(item)

    items.sort(key=lambda item: item["score"], reverse=True)

    db.add(SearchHistory(user_id=current_user.id, search_content=q))
    db.commit()

    return {"items": items}
