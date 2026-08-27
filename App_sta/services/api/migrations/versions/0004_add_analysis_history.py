"""add analysis history

Revision ID: 0004_add_analysis_history
Revises: 0003_add_datasets
Create Date: 2026-08-24
"""
from collections.abc import Sequence
from typing import Union

from alembic import op
import sqlalchemy as sa

revision: str = "0004_add_analysis_history"
down_revision: Union[str, Sequence[str], None] = "0003_add_datasets"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "analysis_history",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("dataset_id", sa.Uuid(), nullable=False),
        sa.Column("analysis_type", sa.String(length=80), nullable=False),
        sa.Column("dataset_name", sa.String(length=255), nullable=False),
        sa.Column("parameters", sa.JSON(), nullable=False),
        sa.Column("results", sa.JSON(), nullable=False),
        sa.Column("engine_version", sa.String(length=30), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["dataset_id"], ["datasets.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_analysis_history_user_id", "analysis_history", ["user_id"], unique=False)
    op.create_index("ix_analysis_history_dataset_id", "analysis_history", ["dataset_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_analysis_history_dataset_id", table_name="analysis_history")
    op.drop_index("ix_analysis_history_user_id", table_name="analysis_history")
    op.drop_table("analysis_history")
