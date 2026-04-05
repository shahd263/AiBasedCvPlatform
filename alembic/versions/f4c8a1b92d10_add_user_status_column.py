"""Add users.status column

Revision ID: f4c8a1b92d10
Revises: 20667739e565
Create Date: 2026-04-05

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "f4c8a1b92d10"
down_revision: Union[str, None] = "20667739e565"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column(
            "status",
            sa.String(length=50),
            nullable=False,
            server_default="active",
        ),
    )
    op.alter_column("users", "status", server_default=None)


def downgrade() -> None:
    op.drop_column("users", "status")
