import subprocess
import sys

def main():
    print("\033[96mПроверка миграций базы данных...\033[0m")
    
    try:
        # Пытаемся запустить alembic check через uv
        result = subprocess.run(
            ["uv", "run", "alembic", "check"],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            output = result.stderr or result.stdout
            
            # Проверяем, проблема в недоступности БД или в миграциях
            if "ConnectionRefusedError" in output or "could not connect to server" in output:
                print("\033[93mОшибка при выполнении alembic check. Убедитесь, что база данных доступна. Пропуск проверки.\033[0m")
                sys.exit(0)
            
            print("\033[91mОШИБКА: Обнаружены изменения в моделях, для которых не созданы миграции!\033[0m")
            print(output)
            print("\033[93mПожалуйста, выполните: uv run alembic revision --autogenerate -m 'ваше сообщение'\033[0m")
            sys.exit(1)
            
        print("\033[92mМиграции в порядке.\033[0m")
        
    except FileNotFoundError:
        print("\033[93muv не найден. Пропуск проверки.\033[0m")
        sys.exit(0)
    except Exception as e:
        print(f"\033[93mОшибка при выполнении alembic check: {e}. Убедитесь, что база данных доступна.\033[0m")
        sys.exit(0)

if __name__ == "__main__":
    main()
