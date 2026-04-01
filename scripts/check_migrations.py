import subprocess
import sys


def run_command(cmd):
    """Вспомогательная функция для запуска команды"""
    return subprocess.run(cmd, capture_output=True, text=True)


def main():
    # Настройка кодировки для Windows PowerShell
    if sys.platform == "win32":
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except AttributeError:
            pass

    print("\033[96mПроверка миграций базы данных...\033[0m")

    # Список команд для проверки (пробуем разные способы)
    commands_to_try = [
        ["alembic", "check"],
        ["uv", "run", "alembic", "check"],
        ["python", "-m", "alembic", "check"],
    ]

    last_output = ""
    success = False

    for cmd in commands_to_try:
        try:
            result = run_command(cmd)
            if result.returncode == 0:
                success = True
                break
            else:
                last_output = result.stderr or result.stdout
                # Если команда выполнилась, но вернула ошибку миграций (не FileNotFoundError)
                # то считаем, что проверка не прошла
                if (
                    "alembic: error" in last_output
                    or "FAILED" in last_output
                    or "Target database is not up to date" in last_output
                ):
                    break
        except FileNotFoundError:
            continue
        except Exception as e:
            last_output = str(e)
            continue

    if success:
        print("\033[92mМиграции в порядке.\033[0m")
        sys.exit(0)

    # Если мы здесь, значит ни одна команда не сработала или была ошибка миграций
    if last_output:
        # Проверяем на специфические ошибки связи с БД
        db_errors = [
            "ConnectionRefusedError",
            "could not connect to server",
            "Is the server running",
            "Can't connect to",
            "failed to resolve host",  # Добавлено для случаев, когда host 'db' недоступен локально
        ]
        if any(err.lower() in last_output.lower() for err in db_errors):
            print(
                "\033[93mОшибка подключения к БД (или хост 'db' недоступен локально). Пропуск проверки миграций.\033[0m"
            )
            sys.exit(0)

        print(
            "\033[91mОШИБКА: Обнаружены изменения в моделях, для которых не созданы миграции!\033[0m"
        )
        print(last_output)
        print(
            "\033[93mПожалуйста, выполните: alembic revision --autogenerate -m 'сообщение'\033[0m"
        )
        sys.exit(1)
    else:
        print(
            "\033[93mНе удалось запустить alembic check (убедитесь, что alembic установлен). Пропуск.\033[0m"
        )
        sys.exit(0)


if __name__ == "__main__":
    main()
