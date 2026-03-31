import importlib
from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from src.core.config import settings

# Создание асинхронного движка
engine = create_async_engine(settings.DATABASE_URL, echo=False, future=True)

# Создание сессии
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# Базовый класс для всех моделей SQLAlchemy
Base = declarative_base()

# --- АВТОМАТИЧЕСКОЕ ОБНАРУЖЕНИЕ И РЕГИСТРАЦИЯ МОДЕЛЕЙ ---
# Это гарантирует, что все модели, унаследованные от Base,
# будут зарегистрированы в Base.metadata до того, как они понадобятся.


def discover_and_register_models():
    """
    Находит и импортирует все файлы models.py в src/modules,
    чтобы SQLAlchemy мог обнаружить все таблицы.
    """
    # Добавляем корень проекта в путь для корректного импорта
    import sys

    sys.path.append(str(Path(__file__).parent.parent.parent))

    modules_path = Path(__file__).parent.parent / "modules"
    for item in modules_path.iterdir():
        if item.is_dir() and (item / "models.py").exists():
            module_name = f"src.modules.{item.name}.models"
            try:
                importlib.import_module(module_name)
            except Exception as e:
                print(f"Could not import model {module_name}: {e}")


# Вызываем функцию при инициализации модуля
discover_and_register_models()


# --- ЗАВИСИМОСТЬ ДЛЯ РОУТЕРОВ ---
async def get_db() -> AsyncSession:
    """
    Зависимость FastAPI для получения сессии базы данных.
    """
    async with SessionLocal() as session:
        yield session
