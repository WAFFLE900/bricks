from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.api.project_access import accessible_projects_query, get_project_access, project_load_options, require_project_owner
from app.db.session import get_db
from app.models.entities import Notification, Project, ProjectMembership, ProjectTypeSort, User
from app.schemas.project import (
    ProjectCreate,
    ProjectMemberInvite,
    ProjectMemberPermissionUpdate,
    ProjectMemberRead,
    ProjectRead,
    ProjectStateUpdate,
    ProjectStatus,
    ProjectTrashUpdate,
    ProjectTypeRename,
)

router = APIRouter()


def _project_query(db: Session, user_id: int, status_name: ProjectStatus):
    query = accessible_projects_query(db, user_id).options(*project_load_options())
    if status_name == "active":
        query = query.filter(Project.project_trashcan.is_(False), Project.project_ended.is_(False))
    elif status_name == "ended":
        query = query.filter(Project.project_trashcan.is_(False), Project.project_ended.is_(True))
    elif status_name == "trash":
        query = query.filter(Project.project_trashcan.is_(True))
    return query.order_by(Project.project_edit_date.desc())


def _ensure_project_type_sort(db: Session, user_id: int, project_type: str | None, project_ended: bool) -> None:
    if not project_type:
        return

    existing = (
        db.query(ProjectTypeSort)
        .filter(
            ProjectTypeSort.user_id == user_id,
            ProjectTypeSort.project_type == project_type,
            ProjectTypeSort.project_ended == project_ended,
        )
        .first()
    )
    if existing is not None:
        return

    next_sort = (
        db.query(func.max(ProjectTypeSort.project_type_sort))
        .filter(ProjectTypeSort.user_id == user_id, ProjectTypeSort.project_ended == project_ended)
        .scalar()
        or 0
    )
    db.add(
        ProjectTypeSort(
            project_type=project_type,
            project_type_sort=int(next_sort) + 1,
            user_id=user_id,
            project_ended=project_ended,
        )
    )


def _serialize_member(user: User, joined_at, role: str, permission: str) -> ProjectMemberRead:
    return ProjectMemberRead(
        user_id=user.id,
        user_name=user.user_name,
        user_email=user.user_email,
        role=role,
        permission=permission,
        can_edit=permission == "edit",
        joined_at=joined_at,
    )


def _serialize_project(project: Project, current_user_id: int) -> ProjectRead:
    membership = next((item for item in project.memberships if item.user_id == current_user_id), None)
    current_user_permission = "owner" if project.user_id == current_user_id else membership.permission

    members = [
        _serialize_member(
            user=project.user,
            joined_at=project.project_creation_date,
            role="owner",
            permission="edit",
        )
    ]
    members.extend(
        _serialize_member(
            user=item.user,
            joined_at=item.created_at,
            role="member",
            permission=item.permission,
        )
        for item in sorted(project.memberships, key=lambda row: (row.permission != "edit", row.user.user_name.lower()))
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
    )


def _create_notification(
    db: Session,
    *,
    actor: User,
    recipient: User,
    project: Project,
    notification_type: str,
    title: str,
    body: str,
) -> None:
    db.add(
        Notification(
            recipient_user_id=recipient.id,
            actor_user_id=actor.id,
            project_id=project.id,
            notification_type=notification_type,
            notification_title=title,
            notification_body=body,
        )
    )


def _get_member_or_404(db: Session, project_id: int, member_user_id: int) -> ProjectMembership:
    membership = (
        db.query(ProjectMembership)
        .filter(ProjectMembership.project_id == project_id, ProjectMembership.user_id == member_user_id)
        .first()
    )
    if membership is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project member not found.")
    return membership


@router.get("/projects", response_model=list[ProjectRead])
def list_projects(
    status_name: ProjectStatus = Query(default="active", alias="status"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[ProjectRead]:
    items = _project_query(db, current_user.id, status_name).all()
    return [_serialize_project(item, current_user.id) for item in items]


@router.get("/projects/{project_id}", response_model=ProjectRead)
def get_project(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ProjectRead:
    access = get_project_access(db, current_user.id, project_id)
    return _serialize_project(access.project, current_user.id)


@router.post("/projects", response_model=ProjectRead, status_code=status.HTTP_201_CREATED)
def create_project(
    payload: ProjectCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ProjectRead:
    project = Project(
        project_name=payload.project_name,
        project_type=payload.project_type,
        project_image=payload.project_image,
        user_id=current_user.id,
        project_edit=payload.project_edit,
        project_visible=payload.project_visible,
        project_comment=payload.project_comment,
    )
    db.add(project)
    _ensure_project_type_sort(db, current_user.id, payload.project_type, False)
    db.commit()
    db.refresh(project)
    return _serialize_project(project, current_user.id)


@router.post("/projects/{project_id}/members", response_model=ProjectRead, status_code=status.HTTP_201_CREATED)
def invite_project_member(
    project_id: int,
    payload: ProjectMemberInvite,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ProjectRead:
    access = get_project_access(db, current_user.id, project_id)
    require_project_owner(access)

    user_email = payload.user_email.strip().lower()
    if not user_email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Member email is required.")

    member = db.query(User).filter(func.lower(User.user_email) == user_email).first()
    if member is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    if member.id == current_user.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You are already the project owner.")

    existing = (
        db.query(ProjectMembership)
        .filter(ProjectMembership.project_id == project_id, ProjectMembership.user_id == member.id)
        .first()
    )
    if existing is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User is already a member of this project.")

    db.add(
        ProjectMembership(
            project_id=project_id,
            user_id=member.id,
            invited_by_user_id=current_user.id,
            permission=payload.permission,
        )
    )

    role_label = "editor" if payload.permission == "edit" else "viewer"
    _create_notification(
        db,
        actor=current_user,
        recipient=member,
        project=access.project,
        notification_type="project_invite",
        title=f"你已加入專案《{access.project.project_name}》",
        body=f"{current_user.user_name} 已將你設為{role_label == 'editor' and '可編輯' or '可觀看'}成員。",
    )

    db.commit()
    refreshed = get_project_access(db, current_user.id, project_id)
    return _serialize_project(refreshed.project, current_user.id)


@router.patch("/projects/{project_id}/members/{member_user_id}", response_model=ProjectRead)
def update_project_member_permission(
    project_id: int,
    member_user_id: int,
    payload: ProjectMemberPermissionUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ProjectRead:
    access = get_project_access(db, current_user.id, project_id)
    require_project_owner(access)

    membership = _get_member_or_404(db, project_id, member_user_id)
    membership.permission = payload.permission
    db.add(membership)

    role_label = "editor" if payload.permission == "edit" else "viewer"
    _create_notification(
        db,
        actor=current_user,
        recipient=membership.user,
        project=access.project,
        notification_type="project_permission_updated",
        title=f"你在《{access.project.project_name}》的權限已更新",
        body=f"{current_user.user_name} 已將你的權限改為{role_label == 'editor' and '可編輯' or '可觀看'}。",
    )

    db.commit()
    refreshed = get_project_access(db, current_user.id, project_id)
    return _serialize_project(refreshed.project, current_user.id)


@router.patch("/projects/{project_id}/state", response_model=ProjectRead)
def update_project_state(
    project_id: int,
    payload: ProjectStateUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ProjectRead:
    access = get_project_access(db, current_user.id, project_id)
    require_project_owner(access)

    project = access.project
    project.project_ended = payload.state == "end"
    _ensure_project_type_sort(db, current_user.id, project.project_type, project.project_ended)
    db.add(project)
    db.commit()
    db.refresh(project)
    return _serialize_project(project, current_user.id)


@router.patch("/projects/{project_id}/trash", response_model=ProjectRead)
def update_project_trash(
    project_id: int,
    payload: ProjectTrashUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ProjectRead:
    access = get_project_access(db, current_user.id, project_id)
    require_project_owner(access)

    project = access.project
    project.project_trashcan = payload.in_trash
    db.add(project)
    db.commit()
    db.refresh(project)
    return _serialize_project(project, current_user.id)


@router.delete("/projects/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Response:
    access = get_project_access(db, current_user.id, project_id)
    require_project_owner(access)
    db.delete(access.project)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/project-types")
def list_project_types(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    rows = (
        db.query(ProjectTypeSort)
        .filter(ProjectTypeSort.user_id == current_user.id)
        .order_by(ProjectTypeSort.project_ended.asc(), ProjectTypeSort.project_type_sort.asc())
        .all()
    )
    return {
        "items": [
            {
                "type_id": row.type_id,
                "project_type": row.project_type,
                "project_type_sort": row.project_type_sort,
                "project_ended": row.project_ended,
            }
            for row in rows
        ]
    }


@router.post("/project-types/rename")
def rename_project_type(
    payload: ProjectTypeRename,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    updated = (
        db.query(Project)
        .filter(Project.user_id == current_user.id, Project.project_type == payload.old_project_type)
        .update({"project_type": payload.project_type})
    )
    if updated == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project type not found.")

    db.query(ProjectTypeSort).filter(
        ProjectTypeSort.user_id == current_user.id,
        ProjectTypeSort.project_type == payload.old_project_type,
    ).update({"project_type": payload.project_type})

    db.commit()
    return {"status": "success", "updated": updated}
