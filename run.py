import argparse
import os
import subprocess
import sys
from pathlib import Path


def parse_args():
    parser = argparse.ArgumentParser(description="Запуск FastAPI приложения с выбором окружения.")
    parser.add_argument(
        "--env",
        type=str,
        choices=["development", "production"],
        default="development",
        help="Окружение для запуска (по умолчанию: development)",
    )
    return parser.parse_args()


def print_step(msg):
    print(f"\n--- {msg} ---")


def print_error(msg):
    print(f"\n ОШИБКА: {msg}")
    sys.exit(1)


def print_success(msg):
    print(f"\n УСПЕХ: {msg}")


def validate_environment(env):
    """Проверка готовности окружения к запуску."""
    print_step(f"Валидация окружения '{env}' перед запуском")

    # 1. Проверка venv
    venv_path = Path("venv")
    if not venv_path.exists():
        print_error(
            "Виртуальное окружение 'venv' не найдено. Сначала запустите: python scripts/deploy.py"
        )

    # 2. Проверка нужного .env файла
    env_file = f".env.{env}"
    if not Path(env_file).exists():
        # Если нет специального файла, проверяем общий .env
        if not Path(".env").exists():
            print_error(
                f"Файл {env_file} или .env не найден. Сначала запустите: python scripts/deploy.py"
            )

    print_success(f"Окружение '{env}' готово к запуску.")


def get_python_path():
    if os.name == "nt":
        return str(Path("venv/Scripts/python.exe"))
    return str(Path("venv/bin/python"))


def run_visualization_server():
    """Запуск сервера визуализации в отдельном процессе."""
    python_path = get_python_path()
    print("Запуск System Map: http://localhost:8080/db_schema.html")

    # Запускаем в фоновом режиме
    try:
        subprocess.Popen(
            [python_path, "scripts/serve_schema.py"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except Exception as e:
        print(f"Предупреждение: Не удалось запустить сервер визуализации: {e}")


def run_app(env):
    python_path = get_python_path()

    # Устанавливаем переменную окружения для конфига
    os.environ["APP_ENV"] = env

    # Запускаем визуализацию перед основным приложением
    run_visualization_server()

    print_step(f"Запуск FastAPI приложения в режиме: {env}")
    print(f"Используемый файл: .env.{env}")
    print("Адрес: http://localhost:8000")
    print("Документация: http://localhost:8000/docs")
    print("Админка: http://localhost:8000/admin")
    print("-" * 30)

    try:
        # Запуск через модуль uvicorn
        subprocess.run(
            [
                python_path,
                "-m",
                "uvicorn",
                "src.main:app",
                "--host",
                "0.0.0.0",
                "--port",
                "8000",
                "--reload",
            ],
            check=True,
        )
    except KeyboardInterrupt:
        print("\nПриложение остановлено пользователем.")
    except Exception as e:
        print_error(f"Ошибка при запуске приложения: {e}")


if __name__ == "__main__":
    args = parse_args()
    validate_environment(args.env)
    run_app(args.env)
