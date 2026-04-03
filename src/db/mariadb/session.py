import importlib
from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from src.core.config import settings

# Создание асинхронного движка для MariaDB
mariadb_engine = create_async_engine(settings.MARIADB_URL, echo=False, future=True)

# Создание сессии для MariaDB
MariaDBSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=mariadb_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# Базовый класс для всех моделей SQLAlchemy MariaDB
MariaDBBase = declarative_base()


def discover_and_register_mariadb_models():
    """
    Рекурсивно находит и импортирует все файлы models.py в src/modules/mariadb,
    чтобы SQLAlchemy мог обнаружить все таблицы для MariaDB.
    """
    modules_path = Path(__file__).parent.parent.parent / "modules" / "mariadb"
    if not modules_path.exists():
        return

    for item in modules_path.rglob("models.py"):
        # Превращаем путь в формат импорта python: src.modules.mariadb...
        relative_path = item.relative_to(modules_path.parent.parent.parent)
        module_name = str(relative_path).replace("\\", ".").replace("/", ".").replace(".py", "")
        try:
            importlib.import_module(module_name)
        except Exception:
            pass


# Вызываем функцию при инициализации модуля
discover_and_register_mariadb_models()


# --- ЗАВИСИМОСТЬ ДЛЯ РОУТЕРОВ ---
async def get_mariadb_db() -> AsyncSession:
    """
    Зависимость FastAPI для получения сессии базы данных MariaDB.
    """
    async with MariaDBSessionLocal() as session:
        yield session
