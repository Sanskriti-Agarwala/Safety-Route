from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class RiskLevel(str, Enum):
    SAFE = "safe"
    MODERATE = "moderate"
    RISKY = "risky"
    DANGEROUS = "dangerous"


class TimeOfDay(str, Enum):
    EARLY_MORNING = "early_morning"  # 4-7am
    MORNING = "morning"              # 7-12pm
    AFTERNOON = "afternoon"          # 12-5pm
    EVENING = "evening"              # 5-8pm
    NIGHT = "night"                  # 8pm-12am
    LATE_NIGHT = "late_night"        # 12am-4am


class SafetyPreference(str, Enum):
    MAXIMUM_SAFETY = "maximum_safety"
    BALANCED = "balanced"
    TIME_PRIORITY = "time_priority"


class RoutePoint(BaseModel):
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    address: Optional[str] = None


class SafetyQueryRequest(BaseModel):
    route_id: Optional[str] = Field(None, description="Optional route identifier")
    start_location: RoutePoint
    end_location: RoutePoint
    waypoints: Optional[List[RoutePoint]] = Field(default=None, description="Intermediate stops")
    travel_time: Optional[datetime] = Field(None, description="Planned travel time (for time-based safety)")
    user_preference: SafetyPreference = Field(SafetyPreference.BALANCED, description="User safety preference")
    check_radius_km: float = Field(1.0, ge=0.1, le=5.0, description="Radius to check for safety reports")
    
    @field_validator('travel_time')
    @classmethod
    def validate_travel_time(cls, v):
        if v and v < datetime.utcnow():
            return datetime.utcnow()
        return v


class RouteSafetyRequest(BaseModel):
    route_data: Dict[str, Any] = Field(..., description="Route information (distance, duration, path)")
    route_points: List[RoutePoint] = Field(..., description="Route coordinates")
    travel_time: Optional[datetime] = None
    user_id: Optional[str] = None
    check_community_reports: bool = Field(True, description="Include community safety reports")
    include_ai_analysis: bool = Field(True, description="Enable AI safety reasoning")


class SafetyFactor(BaseModel):
    factor_name: str
    score: int = Field(..., ge=0, le=100, description="Individual factor score")
    weight: float = Field(..., ge=0.0, le=1.0, description="Factor importance weight")
    description: str


class SafetyScoreResponse(BaseModel):
    risk_score: int = Field(..., ge=0, le=100, description="Overall risk score (0=safe, 100=dangerous)")
    risk_label: RiskLevel
    report_count: int = Field(..., ge=0)
    avg_severity: float = Field(..., ge=0.0, le=5.0)
    is_night_time: bool
    time_context: str
    critical_reports: int = Field(..., ge=0)
    dominant_categories: List[str]
    requires_warning: bool
    night_penalty_applied: int = Field(..., ge=0)
    clustering_detected: bool
    safety_factors: Optional[List[SafetyFactor]] = None


class AIRiskAssessment(BaseModel):
    safety_score: int = Field(..., ge=0, le=100)
    risk_level: RiskLevel
    risk_factors: List[str] = Field(default_factory=list)
    positive_factors: List[str] = Field(default_factory=list)
    night_safety_concern: bool
    recommended_action: str
    explanation: str
    confidence: Optional[float] = Field(None, ge=0.0, le=1.0)


class RouteSegmentSafety(BaseModel):
    segment_index: int
    latitude: float
    longitude: float
    risk_score: int = Field(..., ge=0, le=100)
    risk_label: RiskLevel
    report_count: int
    distance_from_start_km: Optional[float] = None


class RouteSafetyResponse(BaseModel):
    route_id: Optional[str] = None
    overall_risk_score: int = Field(..., ge=0, le=100)
    risk_label: RiskLevel
    avg_segment_risk: int
    max_segment_risk: int
    total_segments: int
    risky_segments: List[int]
    risky_segment_count: int
    segment_details: List[RouteSegmentSafety]
    ai_assessment: Optional[AIRiskAssessment] = None
    requires_alternative: bool = False
    warning_message: Optional[str] = None
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


class RouteComparisonRequest(BaseModel):
    routes: List[Dict[str, Any]] = Field(..., min_length=2, description="Multiple routes to compare")
    context: Dict[str, Any] = Field(default_factory=dict, description="User context and preferences")
    travel_time: Optional[datetime] = None


class RouteRanking(BaseModel):
    route_index: int
    safety_score: int = Field(..., ge=0, le=100)
    pros: List[str]
    cons: List[str]
    estimated_time_minutes: Optional[int] = None
    distance_km: Optional[float] = None


class RouteComparisonResponse(BaseModel):
    recommended_route_index: int
    reasoning: str
    route_rankings: List[RouteRanking]
    safety_tradeoff: str
    user_warning: Optional[str] = None
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


class RerouteCheckRequest(BaseModel):
    current_route: Dict[str, Any]
    new_reports: List[Dict[str, Any]]
    user_location: RoutePoint
    eta_remaining_minutes: int = Field(..., ge=0)


class RerouteDecision(BaseModel):
    should_reroute: bool
    urgency: str = Field(..., description="low|medium|high|critical")
    reason: str
    affected_segment: str
    user_message: str
    alternative_action: str
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


class SafetyZone(BaseModel):
    zone_id: str
    center_latitude: float
    center_longitude: float
    radius_km: float
    risk_level: RiskLevel
    report_count: int
    dominant_threat: Optional[str] = None
    last_updated: str


class SafetyHeatmapRequest(BaseModel):
    center_latitude: float = Field(..., ge=-90, le=90)
    center_longitude: float = Field(..., ge=-180, le=180)
    radius_km: float = Field(5.0, ge=1.0, le=20.0)
    grid_size_km: float = Field(0.5, ge=0.1, le=2.0)
    time_window_hours: int = Field(24, ge=1, le=168)


class SafetyHeatmapResponse(BaseModel):
    center: RoutePoint
    zones: List[SafetyZone]
    total_zones: int
    high_risk_zones: int
    safe_zones: int
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


class SafetyAlertSubscription(BaseModel):
    user_id: str
    subscribed_routes: List[str] = Field(default_factory=list)
    alert_threshold: RiskLevel = RiskLevel.RISKY
    notification_preferences: Dict[str, bool] = Field(
        default_factory=lambda: {
            "email": True,
            "push": True,
            "sms": False
        }
    )


class SafetyAlert(BaseModel):
    alert_id: str
    route_id: str
    risk_level: RiskLevel
    message: str
    affected_area: str
    recommended_action: str
    timestamp: str
    expires_at: Optional[str] = None


class UserSafetyPreferences(BaseModel):
    user_id: str
    safety_priority: SafetyPreference = SafetyPreference.BALANCED
    avoid_categories: List[str] = Field(
        default_factory=list,
        description="Categories to strongly avoid (e.g., 'poor_lighting', 'isolated_area')"
    )
    max_acceptable_risk: int = Field(50, ge=0, le=100, description="Max risk score willing to accept")
    night_mode_enabled: bool = Field(True, description="Extra caution during night hours")
    enable_ai_explanations: bool = Field(True, description="Show AI reasoning for route choices")


class SafetyInsightsRequest(BaseModel):
    area: RoutePoint
    radius_km: float = Field(2.0, ge=0.5, le=10.0)
    time_range_hours: int = Field(24, ge=1, le=168)


class SafetyInsightsResponse(BaseModel):
    area_summary: str
    total_reports: int
    trend: str = Field(..., description="improving|stable|worsening")
    peak_risk_hours: List[int] = Field(default_factory=list, description="Hours of day with most incidents")
    safest_hours: List[int] = Field(default_factory=list)
    category_breakdown: Dict[str, int]
    ai_recommendations: List[str]
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())