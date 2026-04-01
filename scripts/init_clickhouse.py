import os
import time
from datetime import datetime

import clickhouse_connect


def init_clickhouse():
    # Читаем параметры подключения из переменных окружения
    host = os.getenv("CLICKHOUSE_HOST", "clickhouse")
    port = int(os.getenv("CLICKHOUSE_PORT", 8123))
    user = os.getenv("CLICKHOUSE_USER", "default")
    password = os.getenv("CLICKHOUSE_PASSWORD", "password")

    print(f"Connecting to ClickHouse at {host}:{port} as {user}...")

    # Ожидаем готовности ClickHouse (до 10 попыток)
    client = None
    for i in range(10):
        try:
            client = clickhouse_connect.get_client(
                host=host, port=port, username=user, password=password
            )
            break
        except Exception:
            print(f"Waiting for ClickHouse... ({i+1}/10)")
            time.sleep(2)

    if not client:
        print("Failed to connect to ClickHouse. Skipping mock data initialization.")
        return

    print("Connected to ClickHouse. Initializing mock data...")

    # 1. Создаем таблицу для моковых аналитических данных
    client.command(
        """
        CREATE TABLE IF NOT EXISTS mock_analytics_events (
            id UUID,
            event_type String,
            user_id Int32,
            page_url String,
            created_at DateTime
        ) ENGINE = MergeTree()
        ORDER BY created_at
    """
    )

    # 2. Проверяем, пустая ли таблица
    count_result = client.command("SELECT count() FROM mock_analytics_events")

    if count_result == 0:
        # 3. Вставляем моковые данные
        print("Inserting mock data into 'mock_analytics_events'...")

        # Данные в формате списка списков с объектами datetime
        mock_data = [
            [
                "11111111-1111-1111-1111-111111111111",
                "page_view",
                1,
                "/home",
                datetime(2026, 1, 1, 10, 0, 0),
            ],
            [
                "22222222-2222-2222-2222-222222222222",
                "click_button",
                1,
                "/home",
                datetime(2026, 1, 1, 10, 5, 0),
            ],
            [
                "33333333-3333-3333-3333-333333333333",
                "page_view",
                2,
                "/about",
                datetime(2026, 1, 1, 10, 10, 0),
            ],
            [
                "44444444-4444-4444-4444-444444444444",
                "signup",
                2,
                "/signup",
                datetime(2026, 1, 1, 10, 15, 0),
            ],
            [
                "55555555-5555-5555-5555-555555555555",
                "logout",
                1,
                "/profile",
                datetime(2026, 1, 1, 10, 30, 0),
            ],
        ]

        # Вставка данных пачкой
        client.insert(
            "mock_analytics_events",
            mock_data,
            column_names=["id", "event_type", "user_id", "page_url", "created_at"],
        )
        print("Mock data inserted successfully. Table 'mock_analytics_events' is ready.")
    else:
        print(f"Mock data already exists ({count_result} rows). Skipping insertion.")


if __name__ == "__main__":
    init_clickhouse()
