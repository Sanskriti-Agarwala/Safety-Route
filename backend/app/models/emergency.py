from enum import Enum
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class EmergencyType(str, Enum):
    SOS = "SOS"
    MEDICAL = "MEDICAL"
    ACCIDENT = "ACCIDENT"
    HARASSMENT = "HARASSMENT"
    THREAT = "THREAT"
    OTHER = "OTHER"


class EmergencyStatus(str, Enum):
    TRIGGERED = "TRIGGERED"
    IN_PROGRESS = "IN_PROGRESS"
    RESOLVED = "RESOLVED"
    CANCELLED = "CANCELLED"


class EmergencyEvent(BaseModel):
    emergency_id: str
    user_id: str
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    emergency_type: EmergencyType
    status: EmergencyStatus = EmergencyStatus.TRIGGERED
    description: Optional[str] = None
    contacts_notified: list[str] = Field(default_factory=list)
    resolved_at: Optional[datetime] = None