"""add project memberships and notifications

Revision ID: 20260421_0003
Revises: 20260421_0002
Create Date: 2026-04-21 01:20:00
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "20260421_0003"
down_revision = "20260421_0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "project_membership",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("project_id", sa.Integer(), sa.ForeignKey("project.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("invited_by_user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("permission", sa.String(length=16), nullable=False, server_default="view"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("project_id", "user_id", name="uq_project_membership_project_user"),
    )
    op.create_index("ix_project_membership_project_user", "project_membership", ["project_id", "user_id"])
    op.create_index("ix_project_membership_user_id", "project_membership", ["user_id"])

    op.create_table(
        "notification",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("recipient_user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("actor_user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("project_id", sa.Integer(), sa.ForeignKey("project.id", ondelete="CASCADE"), nullable=False),
        sa.Column("notification_type", sa.String(length=64), nullable=False),
        sa.Column("notification_title", sa.String(length=255), nullable=False),
        sa.Column("notification_body", sa.String(length=500), nullable=False),
        sa.Column("is_read", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_notification_recipient_created", "notification", ["recipient_user_id", "created_at"])


def downgrade() -> None:
    op.drop_index("ix_notification_recipient_created", table_name="notification")
    op.drop_table("notification")
    op.drop_index("ix_project_membership_user_id", table_name="project_membership")
    op.drop_index("ix_project_membership_project_user", table_name="project_membership")
    op.drop_table("project_membership")
