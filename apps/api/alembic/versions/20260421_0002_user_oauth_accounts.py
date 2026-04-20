"""add user oauth account fields

Revision ID: 20260421_0002
Revises: 20260420_0001
Create Date: 2026-04-21 00:10:00
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "20260421_0002"
down_revision = "20260420_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("users", sa.Column("user_google_id", sa.String(length=255), nullable=True))
    op.add_column("users", sa.Column("user_facebook_id", sa.String(length=255), nullable=True))
    op.create_index("ix_users_user_google_id", "users", ["user_google_id"], unique=True)
    op.create_index("ix_users_user_facebook_id", "users", ["user_facebook_id"], unique=True)


def downgrade() -> None:
    op.drop_index("ix_users_user_facebook_id", table_name="users")
    op.drop_index("ix_users_user_google_id", table_name="users")
    op.drop_column("users", "user_facebook_id")
    op.drop_column("users", "user_google_id")
