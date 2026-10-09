"""Add server-side refresh token rotation records.

Revision ID: 20261009_0002
Revises: 20261009_0001
"""

from typing import Sequence

import sqlalchemy as sa
from alembic import op


revision: str = "20261009_0002"
down_revision: str | None = "20261009_0001"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    if not sa.inspect(op.get_bind()).has_table("refresh_tokens"):
        op.create_table(
            "refresh_tokens",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column(
                "created_at",
                sa.DateTime(timezone=True),
                server_default=sa.func.now(),
                nullable=False,
            ),
            sa.Column(
                "updated_at",
                sa.DateTime(timezone=True),
                server_default=sa.func.now(),
                nullable=False,
            ),
            sa.Column("jti", sa.String(length=32), nullable=False, unique=True),
            sa.Column("user_id", sa.Integer(), nullable=False),
            sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
            sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
            sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        )
        op.create_index(
            "ix_refresh_tokens_id",
            "refresh_tokens",
            ["id"],
            unique=False,
        )
        op.create_index(
            "ix_refresh_tokens_jti",
            "refresh_tokens",
            ["jti"],
            unique=True,
        )
        op.create_index(
            "ix_refresh_tokens_user_id",
            "refresh_tokens",
            ["user_id"],
            unique=False,
        )


def downgrade() -> None:
    if sa.inspect(op.get_bind()).has_table("refresh_tokens"):
        op.drop_table("refresh_tokens")
