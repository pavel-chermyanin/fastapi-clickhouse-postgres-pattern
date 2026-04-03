from typing import List

from fastapi import APIRouter, Depends, Query

from src.modules.clickhouse.analytics.schemas import AnalyticsData, AnalyticsQuery
from src.modules.clickhouse.analytics.service import analytics_service

router = APIRouter()


@router.get("/", response_model=List[AnalyticsData])
async def get_analytics(
    query_params: AnalyticsQuery = Depends(),
) -> List[AnalyticsData]:
    """
    Получение аналитических данных из ClickHouse.
    """
    return await analytics_service.get_analytics_data(query_params)


@router.get("/event_count", response_model=int)
async def get_event_count(
    event_name: str = Query(..., description="Название события для подсчета"),
) -> int:
    """
    Получение количества событий по названию из ClickHouse.
    """
    return await analytics_service.get_event_count(event_name)
