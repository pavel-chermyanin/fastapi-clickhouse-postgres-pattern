from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src.core.repository import BaseRepository
from src.modules.users.models import User


class UserRepository(BaseRepository[User]):
    """
    Репозиторий для работы с пользователями.
    Расширяет базовый репозиторий специфичными методами.
    """

    def __init__(self):
        super().__init__(User)

    async def get_by_email(self, db: AsyncSession, email: str) -> Optional[User]:
        """
        Поиск пользователя по адресу электронной почты.

        Args:
            db (AsyncSession): Сессия базы данных.
            email (str): Email пользователя.

        Returns:
            Optional[User]: Объект пользователя или None.
        """
        result = await db.execute(select(User).filter(User.email == email))
        return result.scalars().first()


# Глобальный экземпляр репозитория пользователей
user_repository = UserRepository()
