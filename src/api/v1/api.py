from fastapi import APIRouter

from src.modules.users.router import router as user_router

# Основной роутер API v1
api_router = APIRouter()

# Подключение роутеров из модулей
api_router.include_router(user_router, prefix="/users", tags=["users"])
