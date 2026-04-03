from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class AnalyticsData(BaseModel):
    event_name: str
    user_id: Optional[int] = None
    timestamp: datetime
    value: Optional[float] = None
    metadata: Optional[dict] = None


class AnalyticsQuery(BaseModel):
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    event_name: Optional[str] = None
    user_id: Optional[int] = None
    limit: int = 100
    offset: int = 0
