from enum import Enum
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class TripStatus(str, Enum):
    PLANNED = "PLANNED"
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class Trip(BaseModel):
    trip_id: str
    user_id: str
    start_latitude: float = Field(..., ge=-90, le=90)
    start_longitude: float = Field(..., ge=-180, le=180)
    end_latitude: float = Field(..., ge=-90, le=90)
    end_longitude: float = Field(..., ge=-180, le=180)
    start_time: datetime
    end_time: Optional[datetime] = None
    planned_duration_minutes: Optional[int] = None
    actual_duration_minutes: Optional[int] = None
    safety_score: Optional[float] = Field(default=None, ge=0, le=1)
    status: TripStatus = TripStatus.PLANNED
    route_id: Optional[str] = None
    distance_meters: Optional[float] = None
    alerts_triggered: int = Field(default=0, ge=0)