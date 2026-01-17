from fastapi import APIRouter, Query, HTTPException
from typing import List
from datetime import datetime, timedelta
import uuid
import math

from app.schemas.report import ReportCreate, ReportResponse, NearbyReportsResponse

router = APIRouter(prefix="/report", tags=["reports"])

reports_storage: List[dict] = []  # In-memory storage; use a DB in production

@router.post("", response_model=ReportResponse)
async def submit_report(report: ReportCreate):
    report_id = str(uuid.uuid4())
    
    report_data = {
        "id": report_id,
        "latitude": report.latitude,
        "longitude": report.longitude,
        "category": report.category,
        "severity": report.severity,
        "description": report.description,
        "timestamp": datetime.utcnow().isoformat(),  # ISO format is fine for parsing
    }
    
    reports_storage.append(report_data)
    
    return ReportResponse(
        success=True,
        message="Safety report submitted successfully",
        report_id=report_id
    )

@router.get("/nearby", response_model=NearbyReportsResponse)
async def get_nearby_reports(
    lat: float = Query(..., description="Latitude"),
    lon: float = Query(..., description="Longitude"),
    radius_km: float = Query(1.0, description="Search radius in kilometers"),
    hours_ago: int = Query(24, ge=1, le=168, description="Only reports from last N hours")
):
    cutoff_time = datetime.utcnow() - timedelta(hours=hours_ago)
    nearby = []
    
    for report in reports_storage:
        report_time = datetime.fromisoformat(report["timestamp"])
        
        if report_time < cutoff_time:
            continue  # Correctly skips old reports
        
        distance = haversine_distance(
            lat, lon,
            report["latitude"], report["longitude"]
        )
        
        if distance <= radius_km:
            report_age_hours = (datetime.utcnow() - report_time).total_seconds() / 3600
            decay_weight = calculate_report_weight(report_age_hours, max_age_hours=hours_ago)
            
            nearby.append({
                **report,
                "distance_km": round(distance, 2),
                "age_hours": round(report_age_hours, 1),
                "relevance_weight": round(decay_weight, 2)
            })
    
    nearby.sort(key=lambda x: x["distance_km"])  # Sorts by distance (ascending)
    
    area_risk_score = calculate_area_risk_score(nearby)
    
    return NearbyReportsResponse(
        count=len(nearby),
        reports=nearby,
        area_risk_score=area_risk_score
    )

def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371.0  # Earth's radius in km
    
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)
    
    a = math.sin(delta_lat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2)**2
    c = 2 * math.asin(math.sqrt(a))
    
    return R * c  # Correct Haversine formula

def calculate_report_weight(age_hours: float, max_age_hours: int = 48) -> float:
    if age_hours > max_age_hours:
        return 0.0  # Redundant due to time filtering, but harmless
    
    decay_factor = 1.0 - (age_hours / max_age_hours)
    return max(0.0, min(1.0, decay_factor))  # Clamps to [0,1]

def calculate_area_risk_score(nearby_reports: List[dict]) -> int:
    if not nearby_reports:
        return 0  # Handles empty list
    
    weighted_severity_sum = 0.0
    total_weight = 0.0
    
    for report in nearby_reports:
        weight = report.get("relevance_weight", 1.0)
        severity = report.get("severity", 1)  # Assumes severity is numeric
        
        weighted_severity_sum += severity * weight
        total_weight += weight
    
    if total_weight == 0:
        return 0  # Avoids division by zero
    
    avg_weighted_severity = weighted_severity_sum / total_weight
    
    report_density_factor = min(len(nearby_reports) * 8, 50)  # Arbitrary scaling
    severity_factor = avg_weighted_severity * 10  # Arbitrary scaling
    
    area_risk_score = int(report_density_factor + severity_factor)
    
    return min(100, max(0, area_risk_score))  # Clamps to [0,100]