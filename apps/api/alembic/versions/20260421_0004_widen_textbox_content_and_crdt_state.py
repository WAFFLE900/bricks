"""widen textBox_content and add CRDT snapshot column

Revision ID: 20260421_0004
Revises: 20260421_0003
Create Date: 2026-08-02 00:00:00
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "20260421_0004"
down_revision = "20260421_0003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # A6: CRDT-materialized content can exceed the previous 1000-char cap, so widen to TEXT.
    op.alter_column(
        "textBox",
        "textBox_content",
        existing_type=sa.String(length=1000),
        type_=sa.Text(),
        existing_nullable=True,
    )
    # Durable CRDT snapshot so a reconnecting/cold client rehydrates from Postgres after
    # the single free-tier process restarts or spins down.
    op.add_column(
        "textBox",
        sa.Column("textBox_crdt_state", sa.LargeBinary(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("textBox", "textBox_crdt_state")
    op.alter_column(
        "textBox",
        "textBox_content",
        existing_type=sa.Text(),
        type_=sa.String(length=1000),
        existing_nullable=True,
    )
