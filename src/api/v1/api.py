from fastapi import APIRouter

from src.modules.auth.login import router as auth_router
from src.modules.dashboard.sheets import router as sheets_router
from src.modules.users import router as user_router

# Основной роутер API v1
api_router = APIRouter()

# Подключение роутеров из модулей
api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
api_router.include_router(user_router, prefix="/users", tags=["users"])
api_router.include_router(sheets_router, prefix="/sheets", tags=["dashboard"])
