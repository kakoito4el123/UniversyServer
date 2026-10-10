"""Create ecommerce tables and add the user balance.

Revision ID: 20261011_0005
Revises: 20261009_0003
"""

from typing import Sequence

import sqlalchemy as sa
from alembic import op


revision: str = "20261011_0005"
down_revision: str | None = "20261009_0003"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def _create_index_if_missing(
    table_name: str,
    index_name: str,
    column_names: list[str],
    *,
    unique: bool = False,
) -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if not inspector.has_table(table_name):
        return

    columns = {column["name"] for column in inspector.get_columns(table_name)}
    if not set(column_names).issubset(columns):
        return

    indexes = {index["name"] for index in inspector.get_indexes(table_name)}
    if index_name not in indexes:
        op.create_index(
            index_name,
            table_name,
            column_names,
            unique=unique,
        )


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if inspector.has_table("users"):
        user_columns = {
            column["name"] for column in inspector.get_columns("users")
        }
        if "balance" not in user_columns:
            op.add_column(
                "users",
                sa.Column(
                    "balance",
                    sa.Float(),
                    server_default="0.0",
                    nullable=False,
                ),
            )

    inspector = sa.inspect(bind)
    if not inspector.has_table("categories"):
        op.create_table(
            "categories",
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
            sa.Column("app_id", sa.String(length=255), nullable=False),
            sa.Column("name", sa.String(length=255), nullable=False),
            sa.Column("slug", sa.String(length=255), nullable=False),
            sa.Column("parent_id", sa.Integer(), nullable=True),
            sa.Column("image_url", sa.String(), nullable=True),
            sa.Column(
                "is_active",
                sa.Boolean(),
                default=True,
                nullable=False,
            ),
            sa.ForeignKeyConstraint(["parent_id"], ["categories.id"]),
        )

    inspector = sa.inspect(bind)
    if not inspector.has_table("products"):
        op.create_table(
            "products",
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
            sa.Column("app_id", sa.String(length=255), nullable=False),
            sa.Column("category_id", sa.Integer(), nullable=True),
            sa.Column("title", sa.String(length=255), nullable=False),
            sa.Column("description", sa.Text(), nullable=True),
            sa.Column("price", sa.Float(), default=0.0, nullable=False),
            sa.Column(
                "unit",
                sa.String(length=50),
                default="шт",
                server_default="шт",
                nullable=False,
            ),
            sa.Column("stock", sa.Integer(), nullable=True),
            sa.Column("attributes", sa.JSON(), nullable=True),
            sa.Column("main_image_url", sa.String(), nullable=True),
            sa.Column(
                "is_available",
                sa.Boolean(),
                default=True,
                server_default=sa.text("true"),
                nullable=False,
            ),
            sa.Column(
                "is_deleted",
                sa.Boolean(),
                default=False,
                server_default=sa.text("false"),
                nullable=False,
            ),
            sa.ForeignKeyConstraint(["category_id"], ["categories.id"]),
        )

    inspector = sa.inspect(bind)
    if not inspector.has_table("cart_items"):
        op.create_table(
            "cart_items",
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
            sa.Column("app_id", sa.String(length=255), nullable=False),
            sa.Column("user_id", sa.Integer(), nullable=False),
            sa.Column("product_id", sa.Integer(), nullable=False),
            sa.Column("quantity", sa.Integer(), default=1, nullable=False),
            sa.Column("selected_options", sa.JSON(), nullable=True),
            sa.ForeignKeyConstraint(
                ["user_id"],
                ["users.id"],
                ondelete="CASCADE",
            ),
            sa.ForeignKeyConstraint(
                ["product_id"],
                ["products.id"],
                ondelete="CASCADE",
            ),
        )

    inspector = sa.inspect(bind)
    if not inspector.has_table("orders"):
        op.create_table(
            "orders",
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
            sa.Column("app_id", sa.String(length=255), nullable=False),
            sa.Column("user_id", sa.Integer(), nullable=False),
            sa.Column("total_amount", sa.Float(), nullable=False),
            sa.Column(
                "status",
                sa.String(length=32),
                default="NEW",
                server_default="NEW",
                nullable=False,
            ),
            sa.Column("customer_name", sa.String(length=255), nullable=True),
            sa.Column("phone", sa.String(length=64), nullable=True),
            sa.Column("delivery_address", sa.Text(), nullable=True),
            sa.Column("comment", sa.Text(), nullable=True),
            sa.ForeignKeyConstraint(
                ["user_id"],
                ["users.id"],
                ondelete="CASCADE",
            ),
        )

    inspector = sa.inspect(bind)
    if not inspector.has_table("order_items"):
        op.create_table(
            "order_items",
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
            sa.Column("order_id", sa.Integer(), nullable=False),
            sa.Column("product_id", sa.Integer(), nullable=True),
            sa.Column("title_snapshot", sa.String(length=255), nullable=False),
            sa.Column("price_snapshot", sa.Float(), nullable=False),
            sa.Column("quantity", sa.Integer(), default=1, nullable=False),
            sa.Column("selected_options", sa.JSON(), nullable=True),
            sa.ForeignKeyConstraint(
                ["order_id"],
                ["orders.id"],
                ondelete="CASCADE",
            ),
            sa.ForeignKeyConstraint(
                ["product_id"],
                ["products.id"],
                ondelete="SET NULL",
            ),
        )

    inspector = sa.inspect(bind)
    if not inspector.has_table("app_settings"):
        op.create_table(
            "app_settings",
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
            sa.Column("app_id", sa.String(length=255), nullable=False),
            sa.Column(
                "store_name",
                sa.String(length=255),
                default="Мой Магазин",
                server_default="Мой Магазин",
                nullable=False,
            ),
            sa.Column(
                "currency",
                sa.String(length=16),
                default="USD",
                server_default="USD",
                nullable=False,
            ),
            sa.Column(
                "delivery_fee",
                sa.Float(),
                default=0.0,
                server_default="0.0",
                nullable=False,
            ),
            sa.Column(
                "min_order_amount",
                sa.Float(),
                default=0.0,
                server_default="0.0",
                nullable=False,
            ),
            sa.Column(
                "is_active",
                sa.Boolean(),
                default=True,
                server_default=sa.text("true"),
                nullable=False,
            ),
            sa.Column("extra_config", sa.JSON(), nullable=True),
            sa.UniqueConstraint("app_id"),
        )

    for table_name, column_name in (
        ("categories", "id"),
        ("categories", "app_id"),
        ("categories", "slug"),
        ("products", "id"),
        ("products", "app_id"),
        ("products", "title"),
        ("cart_items", "id"),
        ("cart_items", "app_id"),
        ("cart_items", "user_id"),
        ("cart_items", "product_id"),
        ("orders", "id"),
        ("orders", "app_id"),
        ("orders", "user_id"),
        ("order_items", "id"),
        ("order_items", "order_id"),
        ("app_settings", "id"),
    ):
        _create_index_if_missing(
            table_name,
            f"ix_{table_name}_{column_name}",
            [column_name],
        )

    _create_index_if_missing(
        "app_settings",
        "ix_app_settings_app_id",
        ["app_id"],
        unique=True,
    )


def downgrade() -> None:
    bind = op.get_bind()

    for table_name in (
        "order_items",
        "orders",
        "cart_items",
        "products",
        "categories",
        "app_settings",
    ):
        if sa.inspect(bind).has_table(table_name):
            op.drop_table(table_name)

    inspector = sa.inspect(bind)
    if inspector.has_table("users"):
        user_columns = {
            column["name"] for column in inspector.get_columns("users")
        }
        if "balance" in user_columns:
            with op.batch_alter_table("users") as batch_op:
                batch_op.drop_column("balance")
