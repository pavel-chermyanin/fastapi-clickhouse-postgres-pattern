from fastapi import APIRouter

from src.modules.clickhouse.analytics.router import router as analytics_router
from src.modules.mariadb.products.router import router as product_router
from src.modules.postgres.users.router import router as user_router

# Основной роутер API v1
api_router = APIRouter()

# Подключение роутеров из модулей
api_router.include_router(user_router, prefix="/users", tags=["users"])
api_router.include_router(product_router, prefix="/products", tags=["products"])
api_router.include_router(analytics_router, prefix="/analytics", tags=["analytics"])
