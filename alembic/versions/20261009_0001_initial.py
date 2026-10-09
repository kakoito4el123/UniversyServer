"""Начальная схема пользователей и заметок.

Revision ID: 20261009_0001
Revises:
"""

from typing import Sequence

import sqlalchemy as sa
from alembic import op


revision: str = "20261009_0001"
down_revision: str | None = None
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if not inspector.has_table("users"):
        op.create_table(
            "users",
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
            sa.Column("username", sa.String(length=50), nullable=False),
            sa.Column("hashed_password", sa.String(length=255), nullable=False),
            sa.Column("bio", sa.String(), nullable=True),
            sa.Column("avatar_url", sa.String(), nullable=True),
        )
        op.create_index("ix_users_id", "users", ["id"], unique=False)
        op.create_index("ix_users_username", "users", ["username"], unique=True)
    else:
        existing_user_columns = {
            column["name"] for column in sa.inspect(bind).get_columns("users")
        }
        if "bio" not in existing_user_columns:
            op.add_column("users", sa.Column("bio", sa.String(), nullable=True))
        if "avatar_url" not in existing_user_columns:
            op.add_column(
                "users",
                sa.Column("avatar_url", sa.String(), nullable=True),
            )

    inspector = sa.inspect(bind)
    if not inspector.has_table("notes"):
        op.create_table(
            "notes",
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
            sa.Column("title", sa.String(length=255), nullable=False),
            sa.Column("content", sa.Text(), nullable=False),
            sa.Column("user_id", sa.Integer(), nullable=False),
            sa.Column("app_id", sa.String(length=255), nullable=False),
            sa.ForeignKeyConstraint(
                ["user_id"],
                ["users.id"],
                ondelete="CASCADE",
            ),
        )
        op.create_index("ix_notes_id", "notes", ["id"], unique=False)
        op.create_index("ix_notes_user_id", "notes", ["user_id"], unique=False)
        op.create_index("ix_notes_app_id", "notes", ["app_id"], unique=False)


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if inspector.has_table("notes"):
        op.drop_table("notes")
    inspector = sa.inspect(bind)
    if inspector.has_table("users"):
        op.drop_table("users")
