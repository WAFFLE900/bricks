from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, LargeBinary, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    user_password: Mapped[str | None] = mapped_column(String(128), nullable=True)
    user_name: Mapped[str] = mapped_column(String(100))
    user_google_id: Mapped[str | None] = mapped_column(String(255), unique=True, index=True, nullable=True)
    user_facebook_id: Mapped[str | None] = mapped_column(String(255), unique=True, index=True, nullable=True)
    user_purpose: Mapped[str | None] = mapped_column(String(255), nullable=True)
    user_identity: Mapped[str | None] = mapped_column(String(100), nullable=True)
    user_otherTool: Mapped[str | None] = mapped_column(String(255), nullable=True)
    user_avatar: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    projects: Mapped[list["Project"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    project_memberships: Mapped[list["ProjectMembership"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
        foreign_keys="ProjectMembership.user_id",
    )
    records: Mapped[list["Record"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    search_history: Mapped[list["SearchHistory"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    received_notifications: Mapped[list["Notification"]] = relationship(
        back_populates="recipient",
        cascade="all, delete-orphan",
        foreign_keys="Notification.recipient_user_id",
    )
    sent_notifications: Mapped[list["Notification"]] = relationship(
        back_populates="actor",
        cascade="all, delete-orphan",
        foreign_keys="Notification.actor_user_id",
    )

    @property
    def has_password(self) -> bool:
        return bool(self.user_password)

    @property
    def has_google_account(self) -> bool:
        return bool(self.user_google_id)

    @property
    def has_facebook_account(self) -> bool:
        return bool(self.user_facebook_id)

    @property
    def user_purpose_list(self) -> list[str]:
        if not self.user_purpose:
            return []
        return [item.strip() for item in self.user_purpose.split(",") if item.strip()]

    @property
    def user_other_tool_list(self) -> list[str]:
        if not self.user_otherTool:
            return []
        return [item.strip() for item in self.user_otherTool.split(",") if item.strip()]


class ProjectTypeSort(Base):
    __tablename__ = "project_sort"

    type_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_type: Mapped[str] = mapped_column(String(100))
    project_type_sort: Mapped[int] = mapped_column(Integer, default=0)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    project_ended: Mapped[bool] = mapped_column(Boolean, default=False)


class Project(Base):
    __tablename__ = "project"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    project_image: Mapped[str | None] = mapped_column(String(255), nullable=True)
    project_name: Mapped[str] = mapped_column(String(255))
    project_trashcan: Mapped[bool] = mapped_column(Boolean, default=False)
    project_ended: Mapped[bool] = mapped_column(Boolean, default=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    project_edit: Mapped[bool] = mapped_column(Boolean, default=True)
    project_visible: Mapped[bool] = mapped_column(Boolean, default=True)
    project_comment: Mapped[bool] = mapped_column(Boolean, default=True)
    project_creation_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    project_edit_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user: Mapped[User] = relationship(back_populates="projects")
    memberships: Mapped[list["ProjectMembership"]] = relationship(back_populates="project", cascade="all, delete-orphan")
    records: Mapped[list["Record"]] = relationship(back_populates="project", cascade="all, delete-orphan")
    notifications: Mapped[list["Notification"]] = relationship(back_populates="project", cascade="all, delete-orphan")


class ProjectMembership(Base):
    __tablename__ = "project_membership"
    __table_args__ = (UniqueConstraint("project_id", "user_id", name="uq_project_membership_project_user"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("project.id", ondelete="CASCADE"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    invited_by_user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    permission: Mapped[str] = mapped_column(String(16), default="view")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    project: Mapped[Project] = relationship(back_populates="memberships")
    user: Mapped[User] = relationship(back_populates="project_memberships", foreign_keys=[user_id])
    invited_by_user: Mapped[User] = relationship(foreign_keys=[invited_by_user_id])


class Record(Base):
    __tablename__ = "record"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    record_name: Mapped[str] = mapped_column(String(255))
    record_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    record_department: Mapped[str | None] = mapped_column(String(255), nullable=True)
    record_attendances: Mapped[int | None] = mapped_column(Integer, nullable=True)
    record_place: Mapped[str | None] = mapped_column(String(255), nullable=True)
    record_host_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    record_trashcan: Mapped[bool] = mapped_column(Boolean, default=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    project_id: Mapped[int] = mapped_column(ForeignKey("project.id", ondelete="CASCADE"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user: Mapped[User] = relationship(back_populates="records")
    project: Mapped[Project] = relationship(back_populates="records")
    text_boxes: Mapped[list["TextBox"]] = relationship(back_populates="record", cascade="all, delete-orphan")


class TextBox(Base):
    __tablename__ = "textBox"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    textBox_content: Mapped[str | None] = mapped_column(Text, nullable=True)
    # Durable CRDT snapshot (opaque Yjs update blob) backing the in-process collaboration
    # room so a reconnecting/cold client rehydrates from Postgres after restart/spindown.
    textBox_crdt_state: Mapped[bytes | None] = mapped_column(LargeBinary, nullable=True)
    record_id: Mapped[int] = mapped_column(ForeignKey("record.id", ondelete="CASCADE"))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    record: Mapped[Record] = relationship(back_populates="text_boxes")
    tags: Mapped[list["Tag"]] = relationship(secondary="tag_textBox", back_populates="text_boxes")


class Tag(Base):
    __tablename__ = "tag"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    tag_name: Mapped[str] = mapped_column(String(100))
    tag_class: Mapped[str | None] = mapped_column(String(32), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    text_boxes: Mapped[list[TextBox]] = relationship(secondary="tag_textBox", back_populates="tags")


class TagTextBox(Base):
    __tablename__ = "tag_textBox"

    tag_id: Mapped[int] = mapped_column(ForeignKey("tag.id", ondelete="CASCADE"), primary_key=True)
    textBox_id: Mapped[int] = mapped_column(ForeignKey("textBox.id", ondelete="CASCADE"), primary_key=True)


class SearchHistory(Base):
    __tablename__ = "search_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    search_content: Mapped[str] = mapped_column(String(255))
    search_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user: Mapped[User] = relationship(back_populates="search_history")


class Notification(Base):
    __tablename__ = "notification"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    recipient_user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    actor_user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    project_id: Mapped[int] = mapped_column(ForeignKey("project.id", ondelete="CASCADE"))
    notification_type: Mapped[str] = mapped_column(String(64))
    notification_title: Mapped[str] = mapped_column(String(255))
    notification_body: Mapped[str] = mapped_column(String(500))
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    recipient: Mapped[User] = relationship(back_populates="received_notifications", foreign_keys=[recipient_user_id])
    actor: Mapped[User] = relationship(back_populates="sent_notifications", foreign_keys=[actor_user_id])
    project: Mapped[Project] = relationship(back_populates="notifications")
