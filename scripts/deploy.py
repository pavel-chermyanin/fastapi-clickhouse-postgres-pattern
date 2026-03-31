import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

# --- ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ДЛЯ ВЫВОДА В КОНСОЛЬ ---


def print_step(msg):
    """Выводит заголовок текущего этапа развертывания"""
    print(f"\n--- {msg} ---")


def print_error(msg):
    """Выводит сообщение об ошибке и завершает работу скрипта"""
    print(f"\n ОШИБКА: {msg}")
    sys.exit(1)


def print_success(msg):
    """Выводит сообщение об успешном завершении этапа"""
    print(f"\n УСПЕХ: {msg}")


def run_command(command, shell=True, exit_on_error=True):
    """Выполняет системную команду и обрабатывает ошибки ее завершения"""
    try:
        # Запуск команды с проверкой кода возврата (check=True)
        result = subprocess.run(command, shell=shell, check=True, text=True)
        return result
    except subprocess.CalledProcessError:
        # Если команда завершилась неудачно
        if exit_on_error:
            print_error(f"Команда '{command}' завершилась с ошибкой.")
        else:
            print(f"\n ПРЕДУПРЕЖДЕНИЕ: Команда '{command}' не удалась. Продолжаем...")
            return None


def validate_env():
    """Проверяет и создает файлы переменных окружения (.env) при их отсутствии"""
    print_step("Настройка конфигурационных файлов (.env)")

    # Шаблон содержимого файла .env с настройками по умолчанию
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

    # 1. Создаем .env.development для локальной разработки, если файла еще нет
    dev_path = Path(".env.development")
    if not dev_path.exists():
        print("Создаю .env.development с настройками по умолчанию...")
        with open(dev_path, "w", encoding="utf-8") as f:
            f.write(default_env_content)

    # 2. Создаем .env.production для боевого окружения, если файла еще нет
    prod_path = Path(".env.production")
    if not prod_path.exists():
        print("Создаю .env.production с настройками по умолчанию...")
        with open(prod_path, "w", encoding="utf-8") as f:
            # В продакшне отключаем DEBUG и меняем имя окружения
            prod_content = default_env_content.replace("DEBUG=True", "DEBUG=False")
            prod_content = prod_content.replace("ENVIRONMENT=development", "ENVIRONMENT=production")
            f.write(prod_content)

    print_success("Конфигурационные файлы (.env.development, .env.production) готовы.")


def get_venv_python():
    """Возвращает путь к интерпретатору Python внутри виртуального окружения (venv)"""
    if os.name == "nt":  # Если ОС Windows
        return str(Path("venv/Scripts/python.exe"))
    return str(Path("venv/bin/python"))  # Для Linux/macOS


def get_venv_pip():
    """Возвращает путь к пакетному менеджеру pip внутри виртуального окружения (venv)"""
    if os.name == "nt":  # Если ОС Windows
        return str(Path("venv/Scripts/pip.exe"))
    return str(Path("venv/bin/pip"))  # Для Linux/macOS


def wait_for_db(python_path, retries=10, delay=3):
    """Ожидает, пока база данных PostgreSQL станет доступна для подключений"""
    print_step("Ожидание готовности базы данных PostgreSQL")

    # Короткий скрипт на Python для проверки подключения к БД через psycopg
    check_script = """
import psycopg
import sys
try:
    # Попытка подключения к БД с параметрами по умолчанию
    conn = psycopg.connect('postgresql://postgres:postgres@localhost:5432/postgres')
    conn.close()
    sys.exit(0)
except Exception as e:
    sys.exit(1)
"""

    # Пытаемся подключиться i раз (по умолчанию 10 попыток с интервалом в 3 секунды)
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
    """Основная точка входа скрипта развертывания"""
    print_step("Запуск процесса развертывания (Senior Approach: Poetry inside venv)")

    # 1. Проверка и создание файлов окружения (.env)
    validate_env()

    # 2. Создание виртуального окружения (venv), если его еще нет
    print_step("Создание виртуального окружения (venv)")
    if not Path("venv").exists():
        run_command(f"{sys.executable} -m venv venv")
        print_success("Venv создан.")
    else:
        print("Venv уже существует.")

    # 3. Установка инструментов и зависимостей проекта внутри venv
    print_step("Установка Poetry и зависимостей локально")
    python_path = os.path.abspath(get_venv_python())

    # Обновляем сам pip для избежания проблем с установкой пакетов
    run_command(f'"{python_path}" -m pip install --upgrade pip')

    # Устанавливаем poetry непосредственно в созданное виртуальное окружение
    run_command(f'"{python_path}" -m pip install poetry')

    # Настраиваем poetry внутри venv, чтобы он не плодил свои окружения в системе
    run_command(f'"{python_path}" -m poetry config virtualenvs.create false --local')

    # Синхронизируем зависимости двумя способами для максимальной надежности
    print("Синхронизация зависимостей...")

    # Способ А: Обычная установка проекта как пакета (через pip)
    print("Установка через pip install . ...")
    run_command(f'"{python_path}" -m pip install .')

    # Способ Б: Установка строго по файлу poetry.lock (если он есть)
    print("Синхронизация через poetry...")
    run_command(f'"{python_path}" -m poetry install --no-root', exit_on_error=False)

    # Дополнительная проверка установки критически важных библиотек
    print("Проверка наличия критических модулей...")
    modules_to_check = ["alembic", "pydantic_settings", "sqlalchemy", "psycopg", "pre_commit"]
    for mod in modules_to_check:
        try:
            # Пытаемся импортировать модуль через Python из venv
            subprocess.run([python_path, "-c", f"import {mod}"], check=True, capture_output=True)
            print(f"  Модуль {mod} найден.")
        except subprocess.CalledProcessError:
            # Если модуль не найден - пробуем установить его вручную
            print(f"  Модуль {mod} НЕ найден. Установка...")
            if mod == "psycopg":
                run_command(f'"{python_path}" -m pip install "psycopg[binary]"')
            elif mod == "pre_commit":
                run_command(f'"{python_path}" -m pip install pre-commit')
            else:
                run_command(f'"{python_path}" -m pip install {mod.replace("_", "-")}')

    print_success("Все зависимости установлены локально в venv.")

    # 4. Запуск баз данных через Docker Compose
    print_step("Запуск Docker контейнеров")
    if not shutil.which("docker-compose") and not shutil.which("docker"):
        print("Docker не найден. Пропускаю запуск контейнеров.")
    else:
        print("Попытка запустить базы данных через Docker...")
        # Пробуем запустить docker-compose (старый формат) или docker compose (новый формат)
        res = run_command("docker-compose up -d", exit_on_error=False)
        if res is None:
            res = run_command("docker compose up -d", exit_on_error=False)

        if res is None:
            print(
                "\n ВНИМАНИЕ: Не удалось запустить Docker. Убедитесь, что Docker Desktop запущен."
            )

    # 5. Ожидаем доступности БД, прежде чем пытаться менять её структуру
    wait_for_db(python_path)

    # 6. Применяем миграции Alembic для создания/обновления таблиц в PostgreSQL
    print_step("Применение миграций")
    run_command(f'"{python_path}" -m alembic upgrade head')

    # 7. Настройка pre-commit хуков (автопроверки кода перед каждым сохранением изменений)
    print_step("Настройка pre-commit")
    run_command(f'"{python_path}" -m pre_commit install')

    # 8. Генерация данных и запуск визуализации (System Map)
    print_step("Генерация и запуск визуализации (System Map)")
    run_command(f'"{python_path}" scripts/generate_schema.py')

    print_success("Проект успешно развернут!")
    print("\nДля запуска приложения используйте:")
    print("  python run.py")

    print("\n--- Запуск сервера визуализации ---")
    # Запуск сервера просмотра схемы (блокирующая операция)
    run_command(f'"{python_path}" scripts/serve_schema.py', exit_on_error=False)


# Проверка, что скрипт запущен напрямую, а не импортирован как модуль
if __name__ == "__main__":
    main()
