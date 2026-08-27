"""ensure one progress row per user and method

Revision ID: 0006_unique_user_progress_method
Revises: 0005_add_user_progress
Create Date: 2026-08-24
"""
from collections.abc import Sequence
from typing import Union

from alembic import op

revision: str = "0006_unique_user_progress_method"
down_revision: Union[str, Sequence[str], None] = "0005_add_user_progress"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_unique_constraint(
        "uq_user_progress_method", "user_progress", ["user_id", "method_id"]
    )


def downgrade() -> None:
    op.drop_constraint("uq_user_progress_method", "user_progress", type_="unique")
