from typing import Generic, List, Optional, Type, TypeVar

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import declarative_base

SQLAlchemyBase = TypeVar("SQLAlchemyBase", bound=declarative_base())
ModelType = TypeVar("ModelType", bound=SQLAlchemyBase)


class BaseRepository(Generic[ModelType]):
    """
    Базовый класс репозитория с общими CRUD операциями.

    Attributes:
        model (Type[ModelType]): Класс модели SQLAlchemy.
    """

    def __init__(self, model: Type[ModelType]):
        self.model = model

    async def get(self, db: AsyncSession, id: int) -> Optional[ModelType]:
        """
        Получение одной записи по её ID.

        Args:
            db (AsyncSession): Сессия базы данных.
            id (int): Идентификатор записи.

        Returns:
            Optional[ModelType]: Объект модели или None.
        """
        result = await db.execute(select(self.model).filter(self.model.id == id))
        return result.scalars().first()

    async def get_multi(
        self, db: AsyncSession, *, skip: int = 0, limit: int = 100
    ) -> List[ModelType]:
        """
        Получение списка записей с поддержкой пагинации.

        Args:
            db (AsyncSession): Сессия базы данных.
            skip (int): Количество пропускаемых записей.
            limit (int): Максимальное количество возвращаемых записей.

        Returns:
            List[ModelType]: Список объектов моделей.
        """
        result = await db.execute(select(self.model).offset(skip).limit(limit))
        return result.scalars().all()

    async def create(self, db: AsyncSession, *, obj_in: any) -> ModelType:
        """
        Создание новой записи в базе данных.

        Args:
            db (AsyncSession): Сессия базы данных.
            obj_in (any): Pydantic модель с данными для создания.

        Returns:
            ModelType: Созданный объект модели.
        """
        db_obj = self.model(**obj_in.model_dump(exclude={"password"}))
        if hasattr(obj_in, "password"):
            # В реальном приложении пароль должен быть хеширован
            db_obj.hashed_password = obj_in.password
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj
