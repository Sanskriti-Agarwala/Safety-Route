from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


class Location(BaseModel):
    lat: float = Field(..., description="Latitude")
    lng: float = Field(..., description="Longitude")
    address: Optional[str] = Field(None, description="Human-readable address")


class UserProfile(BaseModel):
    gender: Optional[str] = None
    age_group: Optional[str] = None
    travel_mode: Optional[str] = "walking"


class RouteRequest(BaseModel):
    source: Location
    destination: Location
    mode: Optional[str] = "walking"
    time_of_day: Optional[int] = None
    user_profile: Optional[UserProfile] = None
    avoid_tolls: Optional[bool] = False
    avoid_highways: Optional[bool] = False


class UnsafeZone(BaseModel):
    zone_id: str
    type: str
    severity: str
    location: Location
    description: str
    distance_from_start: float


class SafetyDetails(BaseModel):
    crime_score: float = Field(..., ge=0, le=100)
    lighting_score: float = Field(..., ge=0, le=100)
    crowd_score: float = Field(..., ge=0, le=100)
    time_factor: float = Field(..., ge=0, le=1)
    unsafe_zones: List[UnsafeZone] = []
    reasoning: Optional[str] = None


class RouteOption(BaseModel):
    route_id: str
    summary: str
    distance: float
    duration: float
    polyline: str
    safety_score: float = Field(..., ge=0, le=100)
    safety_details: SafetyDetails
    is_safest: bool = False


class RouteResponse(BaseModel):
    routes: List[RouteOption]
    safest_route_id: Optional[str]
    timestamp: datetime


class AlternativeRoutesRequest(BaseModel):
    source: Location
    destination: Location
    mode: Optional[str] = "walking"
    time_of_day: Optional[int] = None
    exclude_route_ids: Optional[List[str]] = []
    min_safety_score: Optional[float] = 50.0