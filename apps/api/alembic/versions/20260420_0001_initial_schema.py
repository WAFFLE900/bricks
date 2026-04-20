"""initial schema

Revision ID: 20260420_0001
Revises:
Create Date: 2026-04-20 03:35:00
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "20260420_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_email", sa.String(length=255), nullable=False, unique=True),
        sa.Column("user_password", sa.String(length=128), nullable=True),
        sa.Column("user_name", sa.String(length=100), nullable=False),
        sa.Column("user_purpose", sa.String(length=255), nullable=True),
        sa.Column("user_identity", sa.String(length=100), nullable=True),
        sa.Column("user_otherTool", sa.String(length=255), nullable=True),
        sa.Column("user_avatar", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "project_sort",
        sa.Column("type_id", sa.Integer(), primary_key=True),
        sa.Column("project_type", sa.String(length=100), nullable=False),
        sa.Column("project_type_sort", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("project_ended", sa.Boolean(), nullable=False, server_default=sa.false()),
    )

    op.create_table(
        "project",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("project_type", sa.String(length=100), nullable=True),
        sa.Column("project_image", sa.String(length=255), nullable=True),
        sa.Column("project_name", sa.String(length=255), nullable=False),
        sa.Column("project_trashcan", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("project_ended", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("project_edit", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("project_visible", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("project_comment", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("project_creation_date", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("project_edit_date", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "record",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("record_name", sa.String(length=255), nullable=False),
        sa.Column("record_date", sa.Date(), nullable=True),
        sa.Column("record_department", sa.String(length=255), nullable=True),
        sa.Column("record_attendances", sa.Integer(), nullable=True),
        sa.Column("record_place", sa.String(length=255), nullable=True),
        sa.Column("record_host_name", sa.String(length=255), nullable=True),
        sa.Column("record_trashcan", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("project_id", sa.Integer(), sa.ForeignKey("project.id", ondelete="CASCADE"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "textBox",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("textBox_content", sa.String(length=1000), nullable=True),
        sa.Column("record_id", sa.Integer(), sa.ForeignKey("record.id", ondelete="CASCADE"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "tag",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("tag_name", sa.String(length=100), nullable=False),
        sa.Column("tag_class", sa.String(length=32), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "tag_textBox",
        sa.Column("tag_id", sa.Integer(), sa.ForeignKey("tag.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("textBox_id", sa.Integer(), sa.ForeignKey("textBox.id", ondelete="CASCADE"), primary_key=True),
    )

    op.create_table(
        "search_history",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("search_content", sa.String(length=255), nullable=False),
        sa.Column("search_time", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_index("ix_project_user_status", "project", ["user_id", "project_trashcan", "project_ended"])
    op.create_index("ix_record_project_trash", "record", ["project_id", "record_trashcan"])


def downgrade() -> None:
    op.drop_index("ix_record_project_trash", table_name="record")
    op.drop_index("ix_project_user_status", table_name="project")
    op.drop_table("search_history")
    op.drop_table("tag_textBox")
    op.drop_table("tag")
    op.drop_table("textBox")
    op.drop_table("record")
    op.drop_table("project")
    op.drop_table("project_sort")
    op.drop_table("users")
