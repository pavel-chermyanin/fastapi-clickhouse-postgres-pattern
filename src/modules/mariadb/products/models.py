from sqlalchemy import Column, DateTime, Float, Integer, String
from sqlalchemy.sql import func

from src.db.mariadb.session import MariaDBBase


class Product(MariaDBBase):
    __tablename__ = "products"
    __table_args__ = {"comment": "Таблица продуктов"}

    id = Column(Integer, primary_key=True, index=True, comment="Уникальный идентификатор продукта")
    name = Column(String(255), nullable=False, comment="Название продукта")
    description = Column(String(1024), comment="Описание продукта")
    price = Column(Float, nullable=False, comment="Цена продукта")
    stock = Column(Integer, nullable=False, default=0, comment="Количество на складе")
    created_at = Column(DateTime, server_default=func.now(), comment="Дата создания продукта")
    updated_at = Column(
        DateTime, onupdate=func.now(), comment="Дата последнего обновления продукта"
    )
