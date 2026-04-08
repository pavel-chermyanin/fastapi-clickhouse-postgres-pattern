"""Initial migration for clean template

Revision ID: 000000000001
Revises:
Create Date: 2026-04-08 12:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "000000000001"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- Таблица USERS ---
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False, comment="Уникальный идентификатор"),
        sa.Column("email", sa.String(), nullable=False, comment="Email пользователя"),
        sa.Column("hashed_password", sa.String(), nullable=False, comment="Хешированный пароль"),
        sa.Column("full_name", sa.String(), nullable=True, comment="Полное имя пользователя"),
        sa.Column("is_active", sa.Boolean(), nullable=True, comment="Флаг активности пользователя"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
            comment="Дата создания записи",
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=True,
            comment="Дата последнего обновления",
        ),
        sa.PrimaryKeyConstraint("id"),
        comment="Таблица пользователей системы",
    )
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)
    op.create_index(op.f("ix_users_id"), "users", ["id"], unique=False)

    # --- Таблица REPORTS ---
    op.create_table(
        "reports",
        sa.Column("id", sa.Integer(), nullable=False, comment="Уникальный идентификатор отчета"),
        sa.Column("title", sa.String(), nullable=False, comment="Название или заголовок отчета"),
        sa.Column(
            "content",
            sa.String(),
            nullable=True,
            comment="Содержимое отчета или ссылка на хранилище",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
            comment="Время создания отчета",
        ),
        sa.PrimaryKeyConstraint("id"),
        comment="Таблица отчетов системы",
    )
    op.create_index(op.f("ix_reports_id"), "reports", ["id"], unique=False)

    # --- Таблица FILTERS ---
    op.create_table(
        "filters",
        sa.Column("id", sa.Integer(), nullable=False, comment="Уникальный идентификатор фильтра"),
        sa.Column(
            "report_id",
            sa.Integer(),
            nullable=False,
            comment="ID отчета, к которому относится фильтр",
        ),
        sa.Column(
            "name",
            sa.String(),
            nullable=False,
            comment='Название фильтра (например, "Период", "Регион")',
        ),
        sa.Column(
            "config", sa.JSON(), nullable=False, comment="Конфигурация фильтра в формате JSON"
        ),
        sa.ForeignKeyConstraint(["report_id"], ["reports.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        comment="Таблица фильтров для отчетов",
    )
    op.create_index(op.f("ix_filters_id"), "filters", ["id"], unique=False)

    # --- Ассоциативная таблица USER_REPORT_ASSOCIATION ---
    op.create_table(
        "user_report_association",
        sa.Column("user_id", sa.Integer(), nullable=False, comment="ID пользователя"),
        sa.Column("report_id", sa.Integer(), nullable=False, comment="ID отчета"),
        sa.ForeignKeyConstraint(["report_id"], ["reports.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("user_id", "report_id"),
        comment="Связь пользователей с отчетами",
        info={"schema_tab": "postgres"},
    )


def downgrade() -> None:
    op.drop_table("user_report_association")
    op.drop_index(op.f("ix_filters_id"), table_name="filters")
    op.drop_table("filters")
    op.drop_index(op.f("ix_reports_id"), table_name="reports")
    op.drop_table("reports")
    op.drop_index(op.f("ix_users_id"), table_name="users")
    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_table("users")
