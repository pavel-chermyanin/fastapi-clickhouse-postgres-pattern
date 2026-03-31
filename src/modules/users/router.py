from typing import Any, List

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.session import get_db
from src.modules.users.schemas import User, UserCreate
from src.modules.users.service import user_service

# Роутер для управления пользователями
router = APIRouter()


@router.get("/", response_model=List[User])
async def read_users(
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Получение списка пользователей.
    Поддерживает пагинацию через skip и limit.
    """
    return await user_service.get_users(db, skip=skip, limit=limit)


@router.post("/", response_model=User, status_code=status.HTTP_201_CREATED)
async def create_user(
    *,
    db: AsyncSession = Depends(get_db),
    user_in: UserCreate,
) -> Any:
    """
    Регистрация нового пользователя.
    Принимает email, пароль и полное имя.
    """
    return await user_service.create_user(db, user_in)


@router.get("/{user_id}", response_model=User)
async def read_user_by_id(
    user_id: int,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Получение информации о конкретном пользователе по его ID.
    """
    return await user_service.get_user(db, user_id)
