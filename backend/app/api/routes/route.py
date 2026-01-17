from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from datetime import datetime

from app.schemas.route import (
    RouteRequest,
    RouteResponse,
    RouteOption,
    SafetyDetails,
    AlternativeRoutesRequest
)
from app.services.maps_service import MapsService
from app.services.safety_score_service import SafetyScoreService
from app.agents.route_generator_agent import RouteGeneratorAgent
from app.agents.safety_reasoning_agent import SafetyReasoningAgent
from app.utils.response_utils import success_response, error_response

router = APIRouter()

# Initialize services
maps_service = MapsService()
safety_service = SafetyScoreService()
route_agent = RouteGeneratorAgent()
safety_agent = SafetyReasoningAgent()


@router.post("/plan", response_model=dict)
async def plan_route(request: RouteRequest):
    """
    Plan routes from source to destination with safety scoring.
    
    Returns multiple route options with safety scores.
    """
    try:
        # Convert Pydantic models to dicts
        source_dict = request.source.dict()
        dest_dict = request.destination.dict()
        
        # Get multiple routes from maps service
        routes = await maps_service.get_routes(
            source=source_dict,
            destination=dest_dict,
            mode=request.mode or "walking"
        )
        
        if not routes:
            raise HTTPException(
                status_code=404,
                detail="No routes found between source and destination"
            )
        
        # Calculate safety score for each route
        route_options = []
        for idx, route in enumerate(routes):
            # Calculate safety score
            safety_score = await safety_service.calculate_safety_score(
                route=route,
                time_of_day=request.time_of_day or datetime.now().hour,
                user_profile=request.user_profile.dict() if request.user_profile else None
            )
            
            # Get unsafe zones along route
            unsafe_zones = await safety_service.get_unsafe_zones(route)
            
            # Get AI reasoning for safety score
            reasoning = await safety_agent.analyze_route_safety(
                route=route,
                safety_score=safety_score,
                unsafe_zones=unsafe_zones
            )
            
            route_option = RouteOption(
                route_id=f"route_{idx + 1}",
                summary=route.get("summary", f"Route {idx + 1}"),
                distance=route.get("distance", 0),
                duration=route.get("duration", 0),
                polyline=route.get("polyline", ""),
                safety_score=safety_score["overall_score"],
                safety_details=SafetyDetails(
                    crime_score=safety_score["crime_score"],
                    lighting_score=safety_score["lighting_score"],
                    crowd_score=safety_score["crowd_score"],
                    time_factor=safety_score["time_factor"],
                    unsafe_zones=unsafe_zones,
                    reasoning=reasoning
                ),
                is_safest=False  # Will be set after comparing all routes
            )
            route_options.append(route_option)
        
        # Mark the safest route
        if route_options:
            safest = max(route_options, key=lambda r: r.safety_score)
            safest.is_safest = True
        
        return success_response(
            data={
                "routes": [r.dict() for r in route_options],
                "safest_route_id": safest.route_id if route_options else None,
                "timestamp": datetime.now().isoformat()
            },
            message=f"Found {len(route_options)} route(s)"
        )
        
    except Exception as e:
        return error_response(
            message=f"Error planning route: {str(e)}",
            status_code=500
        )


@router.get("/safest", response_model=dict)
async def get_safest_route(
    source_lat: float = Query(..., description="Source latitude"),
    source_lng: float = Query(..., description="Source longitude"),
    dest_lat: float = Query(..., description="Destination latitude"),
    dest_lng: float = Query(..., description="Destination longitude"),
    mode: Optional[str] = Query("walking", description="Travel mode"),
    time_of_day: Optional[int] = Query(None, description="Hour of day (0-23)")
):
    """
    Get only the safest route between two points.
    """
    try:
        from app.schemas.route import Location
        
        request = RouteRequest(
            source=Location(lat=source_lat, lng=source_lng),
            destination=Location(lat=dest_lat, lng=dest_lng),
            mode=mode,
            time_of_day=time_of_day
        )
        
        # Use the route planning endpoint
        result = await plan_route(request)
        
        if result.get("success") and result.get("data"):
            routes = result["data"]["routes"]
            safest = next((r for r in routes if r.get("is_safest")), None)
            
            if safest:
                return success_response(
                    data=safest,
                    message="Safest route retrieved successfully"
                )
        
        raise HTTPException(status_code=404, detail="No safe route found")
        
    except Exception as e:
        return error_response(
            message=f"Error finding safest route: {str(e)}",
            status_code=500
        )


@router.post("/alternatives", response_model=dict)
async def get_alternative_routes(request: AlternativeRoutesRequest):
    """
    Get alternative routes excluding specific route IDs or unsafe zones.
    """
    try:
        # Convert to dicts
        source_dict = request.source.dict()
        dest_dict = request.destination.dict()
        
        # Get all routes
        routes = await maps_service.get_routes(
            source=source_dict,
            destination=dest_dict,
            mode=request.mode or "walking",
            alternatives=True,
            max_routes=5
        )
        
        # Filter and score
        alternative_options = []
        for idx, route in enumerate(routes):
            route_id = f"route_{idx + 1}"
            
            # Skip excluded routes
            if request.exclude_route_ids and route_id in request.exclude_route_ids:
                continue
            
            # Calculate safety
            safety_score = await safety_service.calculate_safety_score(
                route=route,
                time_of_day=request.time_of_day or datetime.now().hour
            )
            
            # Skip routes below minimum safety threshold
            if request.min_safety_score and safety_score["overall_score"] < request.min_safety_score:
                continue
            
            unsafe_zones = await safety_service.get_unsafe_zones(route)
            
            route_option = RouteOption(
                route_id=route_id,
                summary=route.get("summary", f"Alternative {len(alternative_options) + 1}"),
                distance=route.get("distance", 0),
                duration=route.get("duration", 0),
                polyline=route.get("polyline", ""),
                safety_score=safety_score["overall_score"],
                safety_details=SafetyDetails(
                    crime_score=safety_score["crime_score"],
                    lighting_score=safety_score["lighting_score"],
                    crowd_score=safety_score["crowd_score"],
                    time_factor=safety_score["time_factor"],
                    unsafe_zones=unsafe_zones
                )
            )
            alternative_options.append(route_option)
        
        return success_response(
            data={
                "alternatives": [r.dict() for r in alternative_options],
                "count": len(alternative_options)
            },
            message=f"Found {len(alternative_options)} alternative route(s)"
        )
        
    except Exception as e:
        return error_response(
            message=f"Error getting alternatives: {str(e)}",
            status_code=500
        )


@router.get("/analyze/{route_id}", response_model=dict)
async def analyze_route(route_id: str):
    """
    Deep analysis of a specific route including all safety factors.
    """
    try:
        # In real implementation, fetch route from cache/database
        # For now, return mock analysis
        
        analysis = {
            "route_id": route_id,
            "detailed_analysis": {
                "crime_analysis": "Low crime area with 2 police stations nearby",
                "lighting_analysis": "Well-lit for 80% of the route",
                "crowd_analysis": "Moderate foot traffic expected",
                "time_recommendations": {
                    "safe_hours": "6 AM - 9 PM",
                    "caution_hours": "9 PM - 11 PM",
                    "avoid_hours": "11 PM - 6 AM"
                }
            },
            "risk_segments": [],
            "safe_stops": ["Police Station - 0.5km", "Hospital - 1.2km"]
        }
        
        return success_response(
            data=analysis,
            message="Route analysis completed"
        )
        
    except Exception as e:
        return error_response(
            message=f"Error analyzing route: {str(e)}",
            status_code=500
        )


@router.post("/validate", response_model=dict)
async def validate_route(
    polyline: str,
    check_safety: bool = True
):
    """
    Validate if a route is safe and provide warnings.
    """
    try:
        # Decode polyline and check for unsafe zones
        route_points = maps_service.decode_polyline(polyline)
        
        warnings = []
        if check_safety:
            # Check each segment
            for i in range(len(route_points) - 1):
                segment_warnings = await safety_service.check_segment_safety(
                    route_points[i],
                    route_points[i + 1]
                )
                warnings.extend(segment_warnings)
        
        is_safe = len(warnings) == 0
        
        return success_response(
            data={
                "is_valid": True,
                "is_safe": is_safe,
                "warnings": warnings,
                "recommendation": "Route is safe" if is_safe else "Consider alternative route"
            },
            message="Route validated"
        )
        
    except Exception as e:
        return error_response(
            message=f"Error validating route: {str(e)}",
            status_code=500
        )