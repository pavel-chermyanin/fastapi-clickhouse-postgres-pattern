from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqladmin import Admin
from sqlalchemy import text

from src.admin.filters import FilterAdmin
from src.admin.reports import ReportAdmin
from src.admin.views import UserAdmin
from src.api.v1.api import api_router
from src.core.config import settings
from src.db.clickhouse.client import clickhouse_client
from src.db.mariadb.session import mariadb_engine
from src.db.postgres.session import postgres_engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Управляет жизненным циклом приложения.
    Проверяет соединения с базами данных при запуске.
    """
    # 1. Проверка PostgreSQL
    try:
        async with postgres_engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
            print("Successfully connected to PostgreSQL")
    except Exception as e:
        print(f"Error connecting to PostgreSQL: {e}")
        # В продакшене можно выбрасывать исключение, чтобы контейнер не запустился
        # raise e

    # 2. Проверка MariaDB (Внешняя)
    try:
        async with mariadb_engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
            print("Successfully connected to MariaDB (External)")
    except Exception as e:
        print(f"Error connecting to MariaDB (External): {e}")

    # 3. Проверка ClickHouse (Внешняя)
    try:
        clickhouse_client.query("SELECT 1")
        print("Successfully connected to ClickHouse (External)")
    except Exception as e:
        print(f"Error connecting to ClickHouse: {e}")

    yield


# Инициализация FastAPI приложения
app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    version=settings.VERSION,
    lifespan=lifespan,
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключение основного роутера API
app.include_router(api_router, prefix=settings.API_V1_STR)

# Инициализация административной панели
admin = Admin(app, postgres_engine)

# Регистрация представлений в админке
admin.add_view(UserAdmin)
admin.add_view(ReportAdmin)
admin.add_view(FilterAdmin)


@app.get("/", tags=["Root"])
async def root():
    """Корневой эндпоинт для проверки работоспособности."""
    return {"message": "Welcome to FastAPI Universal Pattern"}


@app.get("/health", tags=["System"])
async def health_check():
    """Эндпоинт для проверки статуса приложения."""
    return {"status": "ok"}
