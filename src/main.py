from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqladmin import Admin

from src.admin.views import UserAdmin
from src.api.v1.api import api_router
from src.core.config import settings
from src.db.session import engine

# Инициализация FastAPI приложения
app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    version=settings.VERSION,
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
admin = Admin(app, engine)

# Регистрация представлений в админке
admin.add_view(UserAdmin)


@app.get("/", tags=["Root"])
async def root():
    """Корневой эндпоинт для проверки работоспособности."""
    return {"message": "Welcome to FastAPI Universal Pattern"}


@app.get("/health", tags=["System"])
async def health_check():
    """Эндпоинт для проверки статуса приложения."""
    return {"status": "ok"}
