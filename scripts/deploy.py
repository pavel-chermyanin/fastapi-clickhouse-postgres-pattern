import subprocess
import sys
from pathlib import Path


def print_step(msg):
    print(f"\n--- {msg} ---")


def print_success(msg):
    print(f"\n УСПЕХ: {msg}")


def validate_env():
    """Проверяет и создает файлы переменных окружения (.env) при их отсутствии"""
    print_step("Настройка конфигурационных файлов (.env)")

    default_env_content = """# --- ОБЩИЕ НАСТРОЙКИ ---
PROJECT_NAME="FastAPI ClickHouse Postgres Pattern"
ENVIRONMENT="development"
DEBUG=True
VERSION="1.0.0"
API_V1_STR="/api/v1"

# --- POSTGRESQL (Локальная база в Docker) ---
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_HOST=db
POSTGRES_PORT=5432
POSTGRES_DB=postgres

# --- MARIADB (Внешняя база данных) ---
MARIADB_USER=root
MARIADB_PASSWORD=root
MARIADB_HOST=localhost
MARIADB_PORT=3306
MARIADB_DB=mariadb

# --- CLICKHOUSE (Внешняя база данных) ---
CLICKHOUSE_HOST=localhost
CLICKHOUSE_PORT=8123
CLICKHOUSE_USER=default
CLICKHOUSE_PASSWORD=password
CLICKHOUSE_DATABASE=default

# --- БЕЗОПАСНОСТЬ ---
SECRET_KEY="yoursecretkeyhere"
ACCESS_TOKEN_EXPIRE_MINUTES=11520 # 8 дней

# --- АДМИНКА ---
ADMIN_USER=admin
ADMIN_PASSWORD=admin
"""

    # 1. Создаем .env.development
    dev_path = Path(".env.development")
    if not dev_path.exists():
        print("Создаю .env.development с настройками по умолчанию...")
        with open(dev_path, "w", encoding="utf-8") as f:
            f.write(default_env_content)

    # 2. Создаем .env.production
    prod_path = Path(".env.production")
    if not prod_path.exists():
        print("Создаю .env.production с настройками по умолчанию...")
        with open(prod_path, "w", encoding="utf-8") as f:
            prod_content = default_env_content.replace("DEBUG=True", "DEBUG=False")
            prod_content = prod_content.replace("ENVIRONMENT=development", "ENVIRONMENT=production")
            f.write(prod_content)

    # 3. Базовый .env больше не создаем, так как docker-compose будет использовать .env.development/.env.production напрямую
    print_success("Конфигурационные файлы (.env.development, .env.production) готовы.")


def run_docker():
    """Запускает Docker Compose"""
    print_step("Запуск инфраструктуры через Docker Compose")

    # Определяем какой файл окружения использовать (по умолчанию development)
    env_file = ".env.development"
    print(f"Используем файл окружения: {env_file}")

    print("Собираем и запускаем контейнеры (БД + Приложение)...")
    print(
        "Внимание: Первый запуск может занять несколько минут, пока Docker установит все зависимости (uv pip install)."
    )
    print(
        "Миграции и тестовые данные будут применены автоматически при старте контейнера приложения."
    )

    try:
        # Пробуем docker compose (новый формат) с указанием --env-file
        subprocess.run(
            ["docker", "compose", "--env-file", env_file, "up", "-d", "--build"], check=True
        )
    except subprocess.CalledProcessError:
        try:
            # Пробуем docker-compose (старый формат)
            subprocess.run(
                ["docker-compose", "--env-file", env_file, "up", "-d", "--build"], check=True
            )
        except Exception as e:
            print(f"\n ОШИБКА при запуске Docker: {e}")
            print("Убедитесь, что Docker Desktop запущен.")
            sys.exit(1)

    print_success("Контейнеры успешно запущены в фоновом режиме.")
    print("-" * 50)
    print(" ССЫЛКИ НА СЕРВИСЫ:")
    print("  🚀 FastAPI App:     http://localhost:8000")
    print("  📝 Swagger UI:      http://localhost:8000/docs")
    print("  🛠️ SQLAdmin:       http://localhost:8000/admin")
    print("  🗺️ System Map:      http://localhost:8080/db_schema.html")
    print("-" * 50)
    print("\nДождитесь полной готовности сервисов (проверить: docker logs -f fastapi_app)")


def setup_precommit():
    """Настраивает pre-commit хуки (требуется установленный pip или uv)"""
    print_step("Настройка pre-commit хуков (проверки перед коммитом)")
    try:
        # Пробуем использовать uv (рекомендуемый способ)
        print("Попытка установки через uv...")
        subprocess.run(["uv", "pip", "install", "pre-commit"], check=True, capture_output=True)
    except Exception:
        try:
            # Откат к pip, если uv не найден
            print("uv не найден. Установка через pip...")
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "pre-commit"],
                check=True,
                capture_output=True,
            )
        except Exception as e:
            print(f" ПРЕДУПРЕЖДЕНИЕ: Не удалось установить pre-commit: {e}")
            return

    try:
        subprocess.run(["pre-commit", "install"], check=True)
        print_success("Pre-commit хуки успешно установлены.")
    except Exception as e:
        print(f" ПРЕДУПРЕЖДЕНИЕ: Не удалось активировать pre-commit: {e}")


def main():
    print_step("Запуск процесса развертывания (Docker-based)")

    # 1. Создание .env файлов
    validate_env()

    # 2. Настройка Git хуков
    setup_precommit()

    # 3. Запуск Docker Compose (миграции внутри)
    run_docker()


if __name__ == "__main__":
    main()
