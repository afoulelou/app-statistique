"""add user progress

Revision ID: 0005_add_user_progress
Revises: 0004_add_analysis_history
Create Date: 2026-08-24
"""
from collections.abc import Sequence
from typing import Union

from alembic import op
import sqlalchemy as sa

revision: str = "0005_add_user_progress"
down_revision: Union[str, Sequence[str], None] = "0004_add_analysis_history"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "user_progress",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("method_id", sa.String(length=80), nullable=False),
        sa.Column("completion", sa.Integer(), nullable=False),
        sa.Column("score", sa.Float(), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_user_progress_user_id", "user_progress", ["user_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_user_progress_user_id", table_name="user_progress")
    op.drop_table("user_progress")
