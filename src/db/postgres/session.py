import importlib
from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from src.core.config import settings

# Создание асинхронного движка
postgres_engine = create_async_engine(settings.DATABASE_URL, echo=False, future=True)

# Создание сессии
PostgresSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=postgres_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# Базовый класс для всех моделей SQLAlchemy
PostgresBase = declarative_base()

# --- АВТОМАТИЧЕСКОЕ ОБНАРУЖЕНИЕ И РЕГИСТРАЦИЯ МОДЕЛЕЙ ---
# Это гарантирует, что все модели, унаследованные от PostgresBase,
# будут зарегистрированы в PostgresBase.metadata до того, как они понадобятся.


def discover_and_register_postgres_models():
    """
    Рекурсивно находит и импортирует все файлы models.py в src/modules/postgres,
    чтобы SQLAlchemy мог обнаружить все таблицы.
    """
    modules_path = Path(__file__).parent.parent.parent / "modules" / "postgres"
    if not modules_path.exists():
        return

    for item in modules_path.rglob("models.py"):
        # Превращаем путь в формат импорта python: src.modules.postgres...
        relative_path = item.relative_to(modules_path.parent.parent.parent)
        module_name = str(relative_path).replace("\\", ".").replace("/", ".").replace(".py", "")
        try:
            importlib.import_module(module_name)
        except Exception:
            pass


# Вызываем функцию при инициализации модуля
discover_and_register_postgres_models()


# --- ЗАВИСИМОСТЬ ДЛЯ РОУТЕРОВ ---
async def get_postgres_db() -> AsyncSession:
    """
    Зависимость FastAPI для получения сессии базы данных.
    """
    async with PostgresSessionLocal() as session:
        yield session
