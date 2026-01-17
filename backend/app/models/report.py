from enum import Enum
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class ReportType(str, Enum):
    CRIME = "CRIME"
    HARASSMENT = "HARASSMENT"
    HAZARD = "HAZARD"
    SUSPICIOUS_ACTIVITY = "SUSPICIOUS_ACTIVITY"
    POOR_LIGHTING = "POOR_LIGHTING"
    UNSAFE_AREA = "UNSAFE_AREA"
    OTHER = "OTHER"


class ReportStatus(str, Enum):
    SUBMITTED = "SUBMITTED"
    UNDER_REVIEW = "UNDER_REVIEW"
    VERIFIED = "VERIFIED"
    REJECTED = "REJECTED"


class SafetyReport(BaseModel):
    report_id: str
    user_id: str
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    report_type: ReportType
    description: str
    severity: Optional[int] = Field(default=3, ge=1, le=5)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    status: ReportStatus = ReportStatus.SUBMITTED
    image_urls: list[str] = Field(default_factory=list)
    is_anonymous: bool = False