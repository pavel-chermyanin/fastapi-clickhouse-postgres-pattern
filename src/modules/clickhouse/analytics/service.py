import json
from typing import List

from src.db.clickhouse.client import clickhouse_client
from src.modules.clickhouse.analytics.schemas import AnalyticsData, AnalyticsQuery


class AnalyticsService:
    async def get_analytics_data(self, query_params: AnalyticsQuery) -> List[AnalyticsData]:
        base_query = (
            "SELECT event_name, user_id, timestamp, value, metadata FROM analytics_table WHERE 1=1"
        )
        params = {}
        conditions = []

        if query_params.start_date:
            conditions.append("timestamp >= {start_date:DateTime}")
            params["start_date"] = query_params.start_date
        if query_params.end_date:
            conditions.append("timestamp <= {end_date:DateTime}")
            params["end_date"] = query_params.end_date
        if query_params.event_name:
            conditions.append("event_name = {event_name:String}")
            params["event_name"] = query_params.event_name
        if query_params.user_id:
            conditions.append("user_id = {user_id:Int32}")
            params["user_id"] = query_params.user_id

        if conditions:
            base_query += " AND " + " AND ".join(conditions)

        base_query += f" LIMIT {query_params.limit} OFFSET {query_params.offset}"

        result_rows = clickhouse_client.query(base_query, parameters=params)

        # Преобразование результатов в Pydantic модели
        analytics_data_list = []
        for row in result_rows:
            # Предполагаем, что порядок колонок в запросе соответствует порядку в схеме
            # и что metadata хранится как строка JSON в ClickHouse
            event_name, user_id, timestamp, value, metadata_str = row
            metadata = {}
            if metadata_str:
                try:
                    metadata = json.loads(metadata_str)
                except json.JSONDecodeError:
                    pass  # Или обработать ошибку, если JSON некорректен

            analytics_data_list.append(
                AnalyticsData(
                    event_name=event_name,
                    user_id=user_id,
                    timestamp=timestamp,
                    value=value,
                    metadata=metadata,
                )
            )
        return analytics_data_list

    async def get_event_count(self, event_name: str) -> int:
        query = "SELECT count() FROM analytics_table WHERE event_name = {event_name:String}"
        params = {"event_name": event_name}
        result = clickhouse_client.query(query, parameters=params)
        return result[0][0] if result else 0


analytics_service = AnalyticsService()
