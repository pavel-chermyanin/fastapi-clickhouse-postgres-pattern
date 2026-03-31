from typing import Any, Dict, List, Optional

import clickhouse_connect

from src.core.config import settings


class ClickHouseClient:
    """
    Клиент для взаимодействия с ClickHouse.
    Обеспечивает подключение и выполнение запросов.
    """

    def __init__(self):
        """Инициализация параметров подключения на основе настроек проекта."""
        self.host = settings.CLICKHOUSE_HOST
        self.port = settings.CLICKHOUSE_PORT
        self.user = settings.CLICKHOUSE_USER
        self.password = settings.CLICKHOUSE_PASSWORD
        self.database = settings.CLICKHOUSE_DATABASE
        self._client = None

    def get_client(self):
        """
        Ленивая инициализация клиента clickhouse-connect.

        Returns:
            clickhouse_connect.driver.Client: Экземпляр клиента ClickHouse.
        """
        if self._client is None:
            self._client = clickhouse_connect.get_client(
                host=self.host,
                port=self.port,
                username=self.user,
                password=self.password,
                database=self.database,
            )
        return self._client

    def query(self, query: str, parameters: Optional[Dict[str, Any]] = None) -> List[Any]:
        """
        Выполнение SELECT запроса к ClickHouse.

        Args:
            query (str): SQL запрос.
            parameters (Dict, optional): Параметры запроса.

        Returns:
            List[Any]: Список строк результата.
        """
        client = self.get_client()
        result = client.query(query, parameters=parameters)
        return result.result_rows

    def execute(self, query: str, parameters: Optional[Dict[str, Any]] = None):
        """
        Выполнение команды (INSERT, ALTER, и т.д.) в ClickHouse.

        Args:
            query (str): SQL команда.
            parameters (Dict, optional): Параметры команды.
        """
        client = self.get_client()
        client.command(query, parameters=parameters)


# Глобальный экземпляр клиента ClickHouse
clickhouse_client = ClickHouseClient()
