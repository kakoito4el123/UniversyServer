"""Add user roles and soft-delete support for notes.

Revision ID: 20261009_0003
Revises: 20261009_0002
"""

from typing import Sequence

import sqlalchemy as sa
from alembic import op


revision: str = "20261009_0003"
down_revision: str | None = "20261009_0002"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if inspector.has_table("users"):
        user_columns = {column["name"] for column in inspector.get_columns("users")}
        if "role" not in user_columns:
            op.add_column(
                "users",
                sa.Column(
                    "role",
                    sa.String(length=16),
                    server_default="USER",
                    nullable=False,
                ),
            )

    inspector = sa.inspect(bind)
    if inspector.has_table("notes"):
        note_columns = {
            column["name"]: column
            for column in inspector.get_columns("notes")
        }
        indexes = {index["name"] for index in inspector.get_indexes("notes")}

        if "title" in note_columns and "ix_notes_title" not in indexes:
            op.create_index("ix_notes_title", "notes", ["title"], unique=False)
        if "is_deleted" not in note_columns:
            op.add_column(
                "notes",
                sa.Column(
                    "is_deleted",
                    sa.Boolean(),
                    server_default=sa.false(),
                    nullable=False,
                ),
            )
            op.create_index(
                "ix_notes_is_deleted",
                "notes",
                ["is_deleted"],
                unique=False,
            )
        if "content" in note_columns and note_columns["content"]["nullable"] is False:
            with op.batch_alter_table("notes") as batch_op:
                batch_op.alter_column(
                    "content",
                    existing_type=sa.Text(),
                    nullable=True,
                )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if inspector.has_table("notes"):
        note_columns = {
            column["name"] for column in inspector.get_columns("notes")
        }
        indexes = {index["name"] for index in inspector.get_indexes("notes")}
        if "is_deleted" in note_columns:
            if "ix_notes_is_deleted" in indexes:
                op.drop_index("ix_notes_is_deleted", table_name="notes")
            op.drop_column("notes", "is_deleted")
        if "ix_notes_title" in indexes:
            op.drop_index("ix_notes_title", table_name="notes")

    if sa.inspect(bind).has_table("users"):
        if "role" in {column["name"] for column in sa.inspect(bind).get_columns("users")}:
            op.drop_column("users", "role")
