from __future__ import annotations

from dataclasses import dataclass

from fastapi import HTTPException, status
from sqlalchemy import or_
from sqlalchemy.orm import Session, selectinload

from app.models.entities import Project, ProjectMembership


@dataclass(slots=True)
class ProjectAccess:
    project: Project
    membership: ProjectMembership | None = None

    @property
    def permission(self) -> str:
        return "owner" if self.membership is None else self.membership.permission

    @property
    def can_edit(self) -> bool:
        return self.membership is None or self.membership.permission == "edit"

    @property
    def can_manage_members(self) -> bool:
        return self.membership is None


def project_load_options():
    return (
        selectinload(Project.user),
        selectinload(Project.memberships).selectinload(ProjectMembership.user),
    )


def accessible_projects_query(db: Session, user_id: int):
    return (
        db.query(Project)
        .filter(
            or_(
                Project.user_id == user_id,
                Project.memberships.any(ProjectMembership.user_id == user_id),
            )
        )
        .distinct()
    )


def get_project_access(db: Session, user_id: int, project_id: int) -> ProjectAccess:
    project = (
        db.query(Project)
        .options(*project_load_options())
        .filter(Project.id == project_id)
        .first()
    )
    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found.")

    if project.user_id == user_id:
        return ProjectAccess(project=project)

    membership = next((item for item in project.memberships if item.user_id == user_id), None)
    if membership is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found.")

    return ProjectAccess(project=project, membership=membership)


def require_project_owner(access: ProjectAccess) -> None:
    if access.membership is not None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only the project owner can do that.")


def require_project_editor(access: ProjectAccess) -> None:
    if not access.can_edit:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You only have view access to this project.")
