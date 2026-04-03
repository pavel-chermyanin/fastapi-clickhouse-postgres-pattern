from sqlalchemy import JSON, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from src.db.postgres.session import PostgresBase as Base


class Filter(Base):
    """
    Модель фильтра для отчета. Один отчет может иметь несколько фильтров.
    """

    __tablename__ = "filters"
    __table_args__ = {"comment": "Таблица фильтров для отчетов"}

    id = Column(Integer, primary_key=True, index=True, comment="Уникальный идентификатор фильтра")
    report_id = Column(
        Integer,
        ForeignKey("reports.id", ondelete="CASCADE"),
        nullable=False,
        comment="ID отчета, к которому относится фильтр",
    )
    name = Column(String, nullable=False, comment="Название фильтра (например, 'Период', 'Регион')")
    config = Column(JSON, nullable=False, comment="Конфигурация фильтра в формате JSON")

    # Обратная связь с отчетом
    report = relationship("src.modules.reports.models.Report", back_populates="filters")
