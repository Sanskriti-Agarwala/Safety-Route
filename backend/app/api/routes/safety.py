"""
Safety Intelligence API Routes
===============================

This module provides REST API endpoints for querying safety information
about specific geographic locations.

Endpoints:
- GET /safety/area - Get safety assessment for a location
- GET /safety/heatmap - Get safety data for map visualization

Purpose:
These endpoints allow the frontend to:
1. Check safety of a specific location before route planning
2. Display safety heatmaps showing risk zones
3. Get real-time safety assessments based on current conditions

Integration:
- Directly calculates safety scores using imported services
- Generates explanations using imported agents
- Aggregates data from crime zones, lighting, and crowd data

Author: Safety Route Team
Date: January 2026
"""

from fastapi import APIRouter, Query, HTTPException
from typing import Dict, Optional, List
from pydantic import BaseModel, Field

from app.services.safety_score_service import SafetyScoreService
from app.agents.safety_reasoning_agent import SafetyReasoningAgent
from app.utils.response_utils import success_response, error_response
from app.utils.geo_utils import create_location
from app.constants.risk_labels import (
    get_risk_level_from_score,
    get_risk_display_info,
    RISK_COLORS
)
from app.constants.messages import (
    get_safety_warning,
    INFO_REAL_TIME_UPDATE
)


router = APIRouter(prefix="/safety", tags=["Safety Intelligence"])

safety_service = SafetyScoreService()
reasoning_agent = SafetyReasoningAgent()


class SafetyAreaResponse(BaseModel):
    """Response model for area safety check"""
    risk_score: int = Field(..., ge=0, le=100, description="Overall safety score (0-100)")
    risk_level: str = Field(..., description="Risk category (safe/moderate/risky/dangerous)")
    message: str = Field(..., description="Human-readable safety assessment")
    color: Optional[str] = Field(None, description="Color code for UI display")
    recommendations: Optional[List[str]] = Field(None, description="Safety recommendations")


class HeatmapPoint(BaseModel):
    """Single point in safety heatmap"""
    lat: float = Field(..., description="Latitude")
    lng: float = Field(..., description="Longitude")
    score: int = Field(..., ge=0, le=100, description="Safety score")
    risk_level: str = Field(..., description="Risk category")


@router.get(
    "/area",
    response_model=Dict,
    summary="Get Safety Assessment for Location",
    description="Returns comprehensive safety information for a specific geographic location"
)
async def get_area_safety(
    lat: float = Query(..., ge=-90, le=90, description="Latitude of the location"),
    lng: float = Query(..., ge=-180, le=180, description="Longitude of the location"),
    time_of_day: Optional[int] = Query(None, ge=0, le=23, description="Hour of day (0-23) for time-based assessment")
):
    """
    Get safety assessment for a specific location.
    
    This endpoint analyzes safety factors at the given coordinates and returns:
    - Numerical risk score (0-100, higher = safer)
    - Risk level category (safe/moderate/risky/dangerous)
    - Human-readable safety message
    - Visual indicators (color codes)
    - Personalized safety recommendations
    
    Query Parameters:
        lat: Latitude (-90 to 90)
        lng: Longitude (-180 to 180)
        time_of_day: Optional hour (0-23) for time-sensitive assessment
    
    Returns:
        200: Safety assessment data
        400: Invalid coordinates
        500: Service error
    
    Example:
        GET /safety/area?lat=20.2961&lng=85.8245&time_of_day=14
        
        Response:
        {
            "success": true,
            "data": {
                "risk_score": 85,
                "risk_level": "safe",
                "message": "This area is generally safe...",
                "color": "#00C851",
                "recommendations": ["Stay alert", "Keep valuables secure"]
            }
        }
    """
    try:
        location = create_location(lat, lng)
        
        current_hour = time_of_day if time_of_day is not None else 12
        
        safety_data = safety_service.calculate_safety_score(location, current_hour)
        
        risk_score = int(safety_data.get("overall_score", 70))
        
        risk_info = get_risk_display_info(risk_score)
        
        explanation = reasoning_agent.generate_safety_explanation(
            location=location,
            safety_score=risk_score,
            time_of_day=current_hour
        )
        
        warning = get_safety_warning(risk_score)
        message = warning if warning else explanation
        
        return success_response(
            data={
                "risk_score": risk_score,
                "risk_level": risk_info["level"],
                "message": message,
                "color": risk_info["color"],
                "recommendations": risk_info["recommendations"],
                "details": {
                    "crime_score": safety_data.get("crime_score", 80),
                    "lighting_score": safety_data.get("lighting_score", 90),
                    "crowd_score": safety_data.get("crowd_score", 70),
                    "time_factor": safety_data.get("time_factor", 1.0)
                }
            },
            message=INFO_REAL_TIME_UPDATE
        )
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    except Exception as e:
        return error_response(
            message=f"Failed to assess location safety: {str(e)}",
            status_code=500
        )


@router.get(
    "/heatmap",
    response_model=Dict,
    summary="Get Safety Heatmap Data",
    description="Returns grid of safety scores for map visualization"
)
async def get_safety_heatmap(
    lat_min: float = Query(..., ge=-90, le=90, description="Minimum latitude"),
    lat_max: float = Query(..., ge=-90, le=90, description="Maximum latitude"),
    lng_min: float = Query(..., ge=-180, le=180, description="Minimum longitude"),
    lng_max: float = Query(..., ge=-180, le=180, description="Maximum longitude"),
    grid_size: int = Query(10, ge=5, le=50, description="Number of points per dimension"),
    time_of_day: Optional[int] = Query(None, ge=0, le=23, description="Hour for assessment")
):
    """
    Generate safety heatmap data for map visualization.
    
    Creates a grid of safety scores across the specified geographic area.
    Useful for displaying color-coded safety zones on a map.
    
    Query Parameters:
        lat_min, lat_max: Latitude bounds of the area
        lng_min, lng_max: Longitude bounds of the area
        grid_size: Number of sample points (default: 10x10 grid)
        time_of_day: Optional hour for time-sensitive data
    
    Returns:
        200: Array of heatmap points with coordinates and scores
        400: Invalid bounds
        500: Service error
    
    Example:
        GET /safety/heatmap?lat_min=20.29&lat_max=20.31&lng_min=85.82&lng_max=85.84&grid_size=10
        
        Response:
        {
            "success": true,
            "data": {
                "points": [
                    {"lat": 20.29, "lng": 85.82, "score": 85, "risk_level": "safe"},
                    ...
                ],
                "bounds": {...},
                "grid_size": 10
            }
        }
    """
    try:
        if lat_min >= lat_max or lng_min >= lng_max:
            raise ValueError("Invalid bounds: min values must be less than max values")
        
        lat_step = (lat_max - lat_min) / grid_size
        lng_step = (lng_max - lng_min) / grid_size
        
        current_hour = time_of_day if time_of_day is not None else 12
        
        heatmap_points = []
        
        for i in range(grid_size):
            for j in range(grid_size):
                lat = lat_min + (i * lat_step)
                lng = lng_min + (j * lng_step)
                
                location = create_location(lat, lng)
                safety_data = safety_service.calculate_safety_score(location, current_hour)
                score = int(safety_data.get("overall_score", 70))
                risk_level = get_risk_level_from_score(score)
                
                heatmap_points.append({
                    "lat": round(lat, 6),
                    "lng": round(lng, 6),
                    "score": score,
                    "risk_level": risk_level
                })
        
        return success_response(
            data={
                "points": heatmap_points,
                "bounds": {
                    "lat_min": lat_min,
                    "lat_max": lat_max,
                    "lng_min": lng_min,
                    "lng_max": lng_max
                },
                "grid_size": grid_size,
                "total_points": len(heatmap_points)
            },
            message=f"Generated heatmap with {len(heatmap_points)} points"
        )
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    except Exception as e:
        return error_response(
            message=f"Failed to generate heatmap: {str(e)}",
            status_code=500
        )


@router.get(
    "/score",
    response_model=Dict,
    summary="Get Quick Safety Score",
    description="Returns only the numerical safety score (lightweight endpoint)"
)
async def get_quick_score(
    lat: float = Query(..., ge=-90, le=90),
    lng: float = Query(..., ge=-180, le=180),
    time_of_day: Optional[int] = Query(None, ge=0, le=23)
):
    """
    Get quick safety score without detailed analysis.
    
    Lightweight endpoint that returns only the numerical score.
    Useful for performance-critical applications or mobile apps
    that need fast responses.
    
    Query Parameters:
        lat: Latitude
        lng: Longitude
        time_of_day: Optional hour
    
    Returns:
        200: {"score": int, "level": str}
        400: Invalid input
        500: Service error
    """
    try:
        location = create_location(lat, lng)
        current_hour = time_of_day if time_of_day is not None else 12
        
        safety_data = safety_service.calculate_safety_score(location, current_hour)
        score = int(safety_data.get("overall_score", 70))
        level = get_risk_level_from_score(score)
        
        return success_response(
            data={
                "score": score,
                "level": level
            }
        )
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    except Exception as e:
        return error_response(
            message=f"Failed to calculate score: {str(e)}",
            status_code=500
        )