from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime
from enum import Enum


class ReportCategory(str, Enum):
    POOR_LIGHTING = "poor_lighting"
    HARASSMENT = "harassment"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"
    ROADBLOCK = "roadblock"
    ACCIDENT = "accident"
    UNSAFE_AREA = "unsafe_area"
    PROTEST = "protest"
    CRIME_INCIDENT = "crime_incident"
    BROKEN_STREETLIGHT = "broken_streetlight"
    ISOLATED_AREA = "isolated_area"
    OTHER = "other"


class SeverityLevel(int, Enum):
    MINIMAL = 1
    LOW = 2
    MODERATE = 3
    HIGH = 4
    CRITICAL = 5


class ReportCreate(BaseModel):
    latitude: float = Field(..., ge=-90, le=90, description="Latitude coordinate")
    longitude: float = Field(..., ge=-180, le=180, description="Longitude coordinate")
    category: ReportCategory = Field(..., description="Type of safety concern")
    severity: SeverityLevel = Field(..., description="Severity level: 1=minimal, 5=critical")
    description: Optional[str] = Field(None, max_length=500, description="Detailed description of the incident")
    photo_url: Optional[str] = Field(None, description="Optional photo evidence URL")
    user_id: Optional[str] = Field(None, description="Optional reporter user ID for tracking")
    
    @field_validator('description')
    @classmethod
    def validate_description(cls, v):
        if v and len(v.strip()) == 0:
            return None
        return v


class ReportResponse(BaseModel):
    success: bool
    message: str
    report_id: str
    timestamp: Optional[str] = None


class ReportDetail(BaseModel):
    id: str
    latitude: float
    longitude: float
    category: str
    severity: int
    description: Optional[str] = None
    timestamp: str
    distance_km: Optional[float] = None
    age_hours: Optional[float] = None
    relevance_weight: Optional[float] = None


class NearbyReportsResponse(BaseModel):
    count: int
    reports: List[ReportDetail]
    area_risk_score: int = Field(..., ge=0, le=100, description="Aggregated risk score (0=safe, 100=very risky)")
    risk_level: Optional[str] = Field(None, description="Categorical risk: Safe/Moderate/Risky/Dangerous")
    dominant_categories: Optional[List[str]] = Field(None, description="Most common report types in area")
    
    @property
    def is_safe(self) -> bool:
        return self.area_risk_score < 30
    
    @property
    def needs_warning(self) -> bool:
        return self.area_risk_score >= 50


class ReportSummary(BaseModel):
    total_reports: int
    time_range_hours: int
    categories_breakdown: dict
    avg_severity: float
    most_recent_report: Optional[str] = None


class ReportQueryParams(BaseModel):
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    radius_km: float = Field(1.0, ge=0.1, le=10.0, description="Search radius")
    hours_ago: int = Field(24, ge=1, le=168, description="Time window in hours")
    min_severity: Optional[int] = Field(None, ge=1, le=5, description="Filter by minimum severity")
    categories: Optional[List[ReportCategory]] = Field(None, description="Filter by specific categories")