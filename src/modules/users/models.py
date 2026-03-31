from sqlalchemy import Boolean, Column, DateTime, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from src.db.session import Base


class User(Base):
    """
    Модель пользователя для базы данных PostgreSQL.
    Хранит основные данные профиля и информацию для аутентификации.
    """

    __tablename__ = "users"
    __table_args__ = {"comment": "Таблица пользователей системы"}

    id = Column(Integer, primary_key=True, index=True, comment="Уникальный идентификатор")
    email = Column(String, unique=True, index=True, nullable=False, comment="Email пользователя")
    hashed_password = Column(String, nullable=False, comment="Хешированный пароль")
    full_name = Column(String, comment="Полное имя пользователя")
    is_active = Column(Boolean, default=True, comment="Флаг активности пользователя")
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), comment="Дата создания записи"
    )
    updated_at = Column(
        DateTime(timezone=True), onupdate=func.now(), comment="Дата последнего обновления"
    )

    # Связь с отчетами (многие-ко-многим)
    reports = relationship("Report", secondary="user_report_association", back_populates="users")
