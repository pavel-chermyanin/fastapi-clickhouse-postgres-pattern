from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from src.db.session import Base

# Ассоциативная таблица для связи Many-to-Many между User и Report
user_report_association = Table(
    "user_report_association",
    Base.metadata,
    Column(
        "user_id",
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
        comment="ID пользователя",
    ),
    Column(
        "report_id",
        Integer,
        ForeignKey("reports.id", ondelete="CASCADE"),
        primary_key=True,
        comment="ID отчета",
    ),
    comment="Связь пользователей с отчетами",
)


class Report(Base):
    """
    Модель отчета. Может быть доступна многим пользователям.
    """

    __tablename__ = "reports"
    __table_args__ = {"comment": "Таблица отчетов системы"}

    id = Column(Integer, primary_key=True, index=True, comment="Уникальный идентификатор отчета")
    title = Column(String, nullable=False, comment="Название или заголовок отчета")
    content = Column(String, comment="Содержимое отчета или ссылка на хранилище")
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), comment="Время создания отчета"
    )

    # Связь с пользователями (многие-ко-многим)
    users = relationship("User", secondary=user_report_association, back_populates="reports")

    # Связь с фильтрами (один-ко-многим)
    # Используем строковое имя класса и полный путь для избежания циклического импорта
    # @doc: У каждого отчета есть свои собственные фильтры, которые принадлежат только ему
    filters = relationship(
        "src.modules.filters.models.Filter", back_populates="report", cascade="all, delete-orphan"
    )
