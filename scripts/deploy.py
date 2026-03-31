import os
import shutil
import subprocess
import sys
import time
from pathlib import Path


def print_step(msg):
    print(f"\n--- {msg} ---")


def print_error(msg):
    print(f"\n ОШИБКА: {msg}")
    sys.exit(1)


def print_success(msg):
    print(f"\n УСПЕХ: {msg}")


def run_command(command, shell=True, exit_on_error=True):
    try:
        result = subprocess.run(command, shell=shell, check=True, text=True)
        return result
    except subprocess.CalledProcessError:
        if exit_on_error:
            print_error(f"Команда '{command}' завершилась с ошибкой.")
        else:
            print(f"\n ПРЕДУПРЕЖДЕНИЕ: Команда '{command}' не удалась. Продолжаем...")
            return None


def validate_env():
    print_step("Настройка конфигурационных файлов (.env)")

    default_env_content = """# App Config
PROJECT_NAME="FastAPI Universal Pattern"
ENVIRONMENT=development
DEBUG=True

# Database (PostgreSQL)
DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/postgres

# ClickHouse
CLICKHOUSE_HOST=localhost
CLICKHOUSE_PORT=8123
CLICKHOUSE_USER=default
CLICKHOUSE_PASSWORD=
CLICKHOUSE_DATABASE=default

# Admin
ADMIN_USER=admin
ADMIN_PASSWORD=admin
SECRET_KEY=yoursecretkeyhere
"""

    # 1. Создаем .env.development если его нет
    dev_path = Path(".env.development")
    if not dev_path.exists():
        print("Создаю .env.development с настройками по умолчанию...")
        with open(dev_path, "w", encoding="utf-8") as f:
            f.write(default_env_content)

    # 2. Создаем .env.production если его нет
    prod_path = Path(".env.production")
    if not prod_path.exists():
        print("Создаю .env.production с настройками по умолчанию...")
        with open(prod_path, "w", encoding="utf-8") as f:
            # В проде по умолчанию DEBUG=False
            prod_content = default_env_content.replace("DEBUG=True", "DEBUG=False")
            prod_content = prod_content.replace("ENVIRONMENT=development", "ENVIRONMENT=production")
            f.write(prod_content)

    print_success("Конфигурационные файлы (.env.development, .env.production) готовы.")


def get_venv_python():
    if os.name == "nt":
        return str(Path("venv/Scripts/python.exe"))
    return str(Path("venv/bin/python"))


def get_venv_pip():
    if os.name == "nt":
        return str(Path("venv/Scripts/pip.exe"))
    return str(Path("venv/bin/pip"))


def wait_for_db(python_path, retries=10, delay=3):
    print_step("Ожидание готовности базы данных PostgreSQL")
    # Простейший скрипт для проверки подключения
    check_script = """
import psycopg
import sys
try:
    conn = psycopg.connect('postgresql://postgres:postgres@localhost:5432/postgres')
    conn.close()
    sys.exit(0)
except Exception as e:
    sys.exit(1)
"""

    for i in range(retries):
        try:
            result = subprocess.run([python_path, "-c", check_script], capture_output=True)
            if result.returncode == 0:
                print_success("База данных готова!")
                return True
        except Exception:
            pass
        print(f"Попытка {i+1}/{retries}: БД еще не готова, ждем {delay} сек...")
        time.sleep(delay)

    print("\n ВНИМАНИЕ: Не удалось дождаться готовности БД. Миграции могут завершиться с ошибкой.")
    return False


def main():
    print_step("Запуск процесса развертывания (Senior Approach: Poetry inside venv)")

    # 1. Валидация окружения
    validate_env()

    # 2. Создание виртуального окружения
    print_step("Создание виртуального окружения (venv)")
    if not Path("venv").exists():
        run_command(f"{sys.executable} -m venv venv")
        print_success("Venv создан.")
    else:
        print("Venv уже существует.")

    # 3. Установка Poetry и зависимостей локально
    print_step("Установка Poetry и зависимостей локально")
    python_path = os.path.abspath(get_venv_python())

    run_command(f'"{python_path}" -m pip install --upgrade pip')
    # Устанавливаем poetry в сам venv, чтобы он не был глобальным
    run_command(f'"{python_path}" -m pip install poetry')

    # Конфигурируем poetry внутри venv, чтобы он не создавал свои окружения
    run_command(f'"{python_path}" -m poetry config virtualenvs.create false --local')

    # Устанавливаем зависимости
    print("Синхронизация зависимостей...")
    # Пытаемся через poetry, если не выходит - через pip install .
    res = run_command(f'"{python_path}" -m poetry install --no-root', exit_on_error=False)
    if res is None:
        print("Poetry install failed, falling back to pip install .")
        run_command(f'"{python_path}" -m pip install .')

    # Проверка наличия alembic и принудительная установка если пропал
    try:
        subprocess.run([python_path, "-m", "alembic", "--version"], check=True, capture_output=True)
    except subprocess.CalledProcessError:
        print("Alembic не найден в модулях. Принудительная установка...")
        run_command(f'"{python_path}" -m pip install alembic sqlalchemy psycopg[binary]')

    print_success("Все зависимости установлены локально в venv.")

    # 4. Запуск инфраструктуры
    print_step("Запуск Docker контейнеров")
    if not shutil.which("docker-compose") and not shutil.which("docker"):
        print("Docker не найден. Пропускаю запуск контейнеров.")
    else:
        print("Попытка запустить базы данных через Docker...")
        # Не выходим с ошибкой, если Docker не запущен, просто предупреждаем
        res = run_command("docker-compose up -d", exit_on_error=False)
        if res is None:
            res = run_command("docker compose up -d", exit_on_error=False)

        if res is None:
            print(
                "\n ВНИМАНИЕ: Не удалось запустить Docker. Убедитесь, что Docker Desktop запущен."
            )
            print(" Если вы используете внешнюю БД, проигнорируйте это сообщение.")

    # 5. Ожидание готовности БД перед миграциями
    wait_for_db(python_path)

    # 6. Применение миграций
    print_step("Применение миграций")
    run_command(f'"{python_path}" -m alembic upgrade head')

    # 6. Настройка pre-commit
    print_step("Настройка pre-commit")
    run_command(f'"{python_path}" -m pre_commit install')

    # 7. Генерация схемы архитектуры
    print_step("Генерация данных для визуализации (System Map)")
    run_command(f'"{python_path}" scripts/generate_schema.py')

    print_success("Проект успешно развернут!")
    print("\nДля запуска приложения используйте:")
    print("  python run.py")


if __name__ == "__main__":
    main()
