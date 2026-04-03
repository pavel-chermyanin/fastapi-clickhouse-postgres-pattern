from typing import List, Optional

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.postgres.users.models import User
from src.modules.postgres.users.repository import user_repository
from src.modules.postgres.users.schemas import UserCreate


class UserService:
    """
    Сервис для работы с бизнес-логикой пользователей.
    Использует репозиторий для доступа к данным.
    """

    async def get_user(self, db: AsyncSession, user_id: int) -> Optional[User]:
        """
        Получение пользователя по его идентификатору.

        Args:
            db (AsyncSession): Сессия базы данных.
            user_id (int): Идентификатор пользователя.

        Returns:
            Optional[User]: Объект пользователя.

        Raises:
            HTTPException: Если пользователь не найден.
        """
        user = await user_repository.get(db, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь не найден"
            )
        return user

    async def get_users(self, db: AsyncSession, skip: int = 0, limit: int = 100) -> List[User]:
        """
        Получение списка всех пользователей.

        Args:
            db (AsyncSession): Сессия базы данных.
            skip (int): Количество пропускаемых записей.
            limit (int): Максимальное количество записей.

        Returns:
            List[User]: Список пользователей.
        """
        return await user_repository.get_multi(db, skip=skip, limit=limit)

    async def create_user(self, db: AsyncSession, user_in: UserCreate) -> User:
        """
        Создание нового пользователя. Проверяет уникальность email.

        Args:
            db (AsyncSession): Сессия базы данных.
            user_in (UserCreate): Модель данных для создания пользователя.

        Returns:
            User: Созданный объект пользователя.

        Raises:
            HTTPException: Если пользователь с таким email уже существует.
        """
        user = await user_repository.get_by_email(db, user_in.email)
        if user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Пользователь с таким email уже существует.",
            )
        return await user_repository.create(db, obj_in=user_in)


# Глобальный экземпляр сервиса пользователей
user_service = UserService()
