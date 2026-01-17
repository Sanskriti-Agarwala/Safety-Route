"""
Trip Management API Routes
==========================

This module provides REST API endpoints for managing user trip sessions
in the Safety Route application.

Endpoints:
- POST /trip/start - Start a new navigation trip
- POST /trip/end - End an active trip
- GET /trip/status - Get current trip status

Purpose:
Trip tracking allows the application to:
1. Monitor user journey from start to destination
2. Calculate trip duration and statistics
3. Enable real-time location updates during navigation
4. Provide trip summaries and history
5. Support emergency features (SOS during active trips)

Data Storage:
- Trips are stored in-memory (not persisted to database)
- Suitable for demo/hackathon purposes
- In production, would use database storage

Author: Safety Route Team
Date: January 2026
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, Optional
from datetime import datetime
import uuid

from app.utils.response_utils import success_response, error_response


router = APIRouter(prefix="/trip", tags=["Trip Management"])


trips_db: Dict[str, Dict] = {}


class TripStartRequest(BaseModel):
    """Request model for starting a new trip"""
    user_id: str = Field(..., description="Unique identifier for the user")
    source: str = Field(..., description="Starting location description")
    destination: str = Field(..., description="Destination location description")
    source_lat: Optional[float] = Field(None, ge=-90, le=90, description="Source latitude")
    source_lng: Optional[float] = Field(None, ge=-180, le=180, description="Source longitude")
    dest_lat: Optional[float] = Field(None, ge=-90, le=90, description="Destination latitude")
    dest_lng: Optional[float] = Field(None, ge=-180, le=180, description="Destination longitude")


class TripEndRequest(BaseModel):
    """Request model for ending a trip"""
    trip_id: str = Field(..., description="Unique trip identifier")
    end_lat: Optional[float] = Field(None, ge=-90, le=90, description="Final latitude")
    end_lng: Optional[float] = Field(None, ge=-180, le=180, description="Final longitude")


class TripUpdateRequest(BaseModel):
    """Request model for updating trip location"""
    trip_id: str = Field(..., description="Unique trip identifier")
    current_lat: float = Field(..., ge=-90, le=90, description="Current latitude")
    current_lng: float = Field(..., ge=-180, le=180, description="Current longitude")


@router.post(
    "/start",
    response_model=Dict,
    summary="Start a New Trip",
    description="Initialize a new navigation trip session with source and destination"
)
async def start_trip(request: TripStartRequest):
    """
    Start a new trip and receive a unique trip ID for tracking.
    
    This endpoint creates a new trip session that can be tracked in real-time.
    The trip_id returned should be used for all subsequent trip operations
    (updates, ending, SOS alerts, etc.).
    
    Request Body:
        user_id: User identifier
        source: Starting location (address or description)
        destination: Target location (address or description)
        source_lat/lng: Optional precise coordinates for source
        dest_lat/lng: Optional precise coordinates for destination
    
    Returns:
        200: Trip started successfully with trip_id
        400: Invalid input
        500: Server error
    
    Example:
        POST /trip/start
        {
            "user_id": "user_123",
            "source": "KIIT University",
            "destination": "Bhubaneswar Railway Station",
            "source_lat": 20.2961,
            "source_lng": 85.8245,
            "dest_lat": 20.2521,
            "dest_lng": 85.8156
        }
        
        Response:
        {
            "success": true,
            "data": {
                "trip_id": "trip_abc123xyz",
                "user_id": "user_123",
                "source": "KIIT University",
                "destination": "Bhubaneswar Railway Station",
                "started_at": "2026-01-17T14:30:00",
                "status": "active"
            },
            "message": "Trip started successfully"
        }
    """
    try:
        trip_id = f"trip_{uuid.uuid4().hex[:12]}"
        
        start_time = datetime.now()
        
        trip_data = {
            "trip_id": trip_id,
            "user_id": request.user_id,
            "source": request.source,
            "destination": request.destination,
            "source_coordinates": {
                "lat": request.source_lat,
                "lng": request.source_lng
            } if request.source_lat and request.source_lng else None,
            "destination_coordinates": {
                "lat": request.dest_lat,
                "lng": request.dest_lng
            } if request.dest_lat and request.dest_lng else None,
            "started_at": start_time.isoformat(),
            "ended_at": None,
            "status": "active",
            "current_location": None,
            "location_updates": []
        }
        
        trips_db[trip_id] = trip_data
        
        return success_response(
            data={
                "trip_id": trip_id,
                "user_id": request.user_id,
                "source": request.source,
                "destination": request.destination,
                "started_at": start_time.isoformat(),
                "status": "active"
            },
            message="Trip started successfully"
        )
    
    except Exception as e:
        return error_response(
            message=f"Failed to start trip: {str(e)}",
            status_code=500
        )


@router.post(
    "/end",
    response_model=Dict,
    summary="End an Active Trip",
    description="Mark a trip as completed and calculate trip statistics"
)
async def end_trip(request: TripEndRequest):
    """
    End an active trip and get trip summary.
    
    This endpoint marks the trip as completed, calculates duration,
    and returns trip statistics. The trip data remains in memory
    for potential history/analytics queries.
    
    Request Body:
        trip_id: The unique trip identifier from start_trip
        end_lat/lng: Optional final location coordinates
    
    Returns:
        200: Trip ended successfully with summary
        404: Trip not found
        400: Trip already ended
        500: Server error
    
    Example:
        POST /trip/end
        {
            "trip_id": "trip_abc123xyz",
            "end_lat": 20.2521,
            "end_lng": 85.8156
        }
        
        Response:
        {
            "success": true,
            "data": {
                "trip_id": "trip_abc123xyz",
                "duration_minutes": 25,
                "started_at": "2026-01-17T14:30:00",
                "ended_at": "2026-01-17T14:55:00",
                "status": "completed"
            },
            "message": "Trip ended successfully. Duration: 25 minutes"
        }
    """
    try:
        trip_id = request.trip_id
        
        if trip_id not in trips_db:
            raise HTTPException(
                status_code=404,
                detail=f"Trip {trip_id} not found"
            )
        
        trip = trips_db[trip_id]
        
        if trip["status"] == "completed":
            raise HTTPException(
                status_code=400,
                detail=f"Trip {trip_id} is already completed"
            )
        
        end_time = datetime.now()
        start_time = datetime.fromisoformat(trip["started_at"])
        
        duration_seconds = (end_time - start_time).total_seconds()
        duration_minutes = int(duration_seconds / 60)
        
        trip["ended_at"] = end_time.isoformat()
        trip["status"] = "completed"
        trip["duration_minutes"] = duration_minutes
        
        if request.end_lat and request.end_lng:
            trip["end_coordinates"] = {
                "lat": request.end_lat,
                "lng": request.end_lng
            }
        
        return success_response(
            data={
                "trip_id": trip_id,
                "duration_minutes": duration_minutes,
                "started_at": trip["started_at"],
                "ended_at": end_time.isoformat(),
                "status": "completed",
                "source": trip["source"],
                "destination": trip["destination"]
            },
            message=f"Trip ended successfully. Duration: {duration_minutes} minutes"
        )
    
    except HTTPException:
        raise
    
    except Exception as e:
        return error_response(
            message=f"Failed to end trip: {str(e)}",
            status_code=500
        )


@router.post(
    "/update-location",
    response_model=Dict,
    summary="Update Current Trip Location",
    description="Update the current location during an active trip for real-time tracking"
)
async def update_trip_location(request: TripUpdateRequest):
    """
    Update current location during an active trip.
    
    This endpoint allows real-time location tracking during navigation.
    Location updates can be sent periodically (e.g., every 30 seconds)
    to track user progress and enable safety monitoring.
    
    Request Body:
        trip_id: Active trip identifier
        current_lat: Current latitude
        current_lng: Current longitude
    
    Returns:
        200: Location updated successfully
        404: Trip not found
        400: Trip not active
        500: Server error
    
    Example:
        POST /trip/update-location
        {
            "trip_id": "trip_abc123xyz",
            "current_lat": 20.2750,
            "current_lng": 85.8200
        }
        
        Response:
        {
            "success": true,
            "data": {
                "trip_id": "trip_abc123xyz",
                "current_location": {"lat": 20.2750, "lng": 85.8200},
                "updated_at": "2026-01-17T14:40:00",
                "total_updates": 5
            },
            "message": "Location updated successfully"
        }
    """
    try:
        trip_id = request.trip_id
        
        if trip_id not in trips_db:
            raise HTTPException(
                status_code=404,
                detail=f"Trip {trip_id} not found"
            )
        
        trip = trips_db[trip_id]
        
        if trip["status"] != "active":
            raise HTTPException(
                status_code=400,
                detail=f"Trip {trip_id} is not active (status: {trip['status']})"
            )
        
        current_location = {
            "lat": request.current_lat,
            "lng": request.current_lng,
            "timestamp": datetime.now().isoformat()
        }
        
        trip["current_location"] = current_location
        trip["location_updates"].append(current_location)
        
        return success_response(
            data={
                "trip_id": trip_id,
                "current_location": {
                    "lat": request.current_lat,
                    "lng": request.current_lng
                },
                "updated_at": current_location["timestamp"],
                "total_updates": len(trip["location_updates"])
            },
            message="Location updated successfully"
        )
    
    except HTTPException:
        raise
    
    except Exception as e:
        return error_response(
            message=f"Failed to update location: {str(e)}",
            status_code=500
        )


@router.get(
    "/status/{trip_id}",
    response_model=Dict,
    summary="Get Trip Status",
    description="Retrieve current status and details of a trip"
)
async def get_trip_status(trip_id: str):
    """
    Get the current status and details of a trip.
    
    Returns comprehensive information about an active or completed trip,
    including duration, locations, and status.
    
    Path Parameters:
        trip_id: Unique trip identifier
    
    Returns:
        200: Trip details
        404: Trip not found
        500: Server error
    
    Example:
        GET /trip/status/trip_abc123xyz
        
        Response:
        {
            "success": true,
            "data": {
                "trip_id": "trip_abc123xyz",
                "user_id": "user_123",
                "status": "active",
                "source": "KIIT University",
                "destination": "Bhubaneswar Railway Station",
                "started_at": "2026-01-17T14:30:00",
                "current_location": {"lat": 20.2750, "lng": 85.8200},
                "duration_so_far_minutes": 10
            }
        }
    """
    try:
        if trip_id not in trips_db:
            raise HTTPException(
                status_code=404,
                detail=f"Trip {trip_id} not found"
            )
        
        trip = trips_db[trip_id]
        
        response_data = {
            "trip_id": trip["trip_id"],
            "user_id": trip["user_id"],
            "status": trip["status"],
            "source": trip["source"],
            "destination": trip["destination"],
            "started_at": trip["started_at"],
            "ended_at": trip.get("ended_at"),
            "current_location": trip.get("current_location"),
            "total_location_updates": len(trip["location_updates"])
        }
        
        if trip["status"] == "active":
            start_time = datetime.fromisoformat(trip["started_at"])
            current_time = datetime.now()
            duration_seconds = (current_time - start_time).total_seconds()
            response_data["duration_so_far_minutes"] = int(duration_seconds / 60)
        else:
            response_data["duration_minutes"] = trip.get("duration_minutes", 0)
        
        return success_response(
            data=response_data,
            message="Trip details retrieved successfully"
        )
    
    except HTTPException:
        raise
    
    except Exception as e:
        return error_response(
            message=f"Failed to get trip status: {str(e)}",
            status_code=500
        )


@router.get(
    "/active/{user_id}",
    response_model=Dict,
    summary="Get Active Trips for User",
    description="Retrieve all active trips for a specific user"
)
async def get_active_trips(user_id: str):
    """
    Get all active trips for a user.
    
    Useful for checking if a user has an ongoing trip before starting
    a new one, or for displaying current navigation sessions.
    
    Path Parameters:
        user_id: User identifier
    
    Returns:
        200: List of active trips (may be empty)
        500: Server error
    
    Example:
        GET /trip/active/user_123
        
        Response:
        {
            "success": true,
            "data": {
                "user_id": "user_123",
                "active_trips": [
                    {
                        "trip_id": "trip_abc123xyz",
                        "source": "KIIT University",
                        "destination": "Bhubaneswar Railway Station",
                        "started_at": "2026-01-17T14:30:00"
                    }
                ],
                "count": 1
            }
        }
    """
    try:
        active_trips = [
            {
                "trip_id": trip["trip_id"],
                "source": trip["source"],
                "destination": trip["destination"],
                "started_at": trip["started_at"],
                "current_location": trip.get("current_location")
            }
            for trip in trips_db.values()
            if trip["user_id"] == user_id and trip["status"] == "active"
        ]
        
        return success_response(
            data={
                "user_id": user_id,
                "active_trips": active_trips,
                "count": len(active_trips)
            },
            message=f"Found {len(active_trips)} active trip(s)"
        )
    
    except Exception as e:
        return error_response(
            message=f"Failed to get active trips: {str(e)}",
            status_code=500
        )