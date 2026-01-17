"""
User Profile Management API Routes
===================================

This module provides REST API endpoints for managing user profiles and preferences
in the Safety Route application.

Endpoints:
- POST /user/create - Create a new user profile
- GET /user/{user_id} - Retrieve user profile
- PUT /user/{user_id}/preferences - Update user preferences
- POST /user/{user_id}/contacts - Add emergency contact

Purpose:
User profiles enable:
1. Personalized route recommendations based on preferences
2. Emergency contact management for SOS features
3. Travel mode defaults (walking, biking, driving)
4. Safety preference settings (e.g., avoid night travel)

Data Storage:
- Users are stored in-memory (not persisted to database)
- Suitable for demo/hackathon purposes
- In production, would use database with authentication

Author: Safety Route Team
Date: January 2026
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, validator
from typing import Dict, Optional, List

from app.utils.response_utils import success_response, error_response


router = APIRouter(prefix="/user", tags=["User Management"])


users_db: Dict[str, Dict] = {}


class UserCreateRequest(BaseModel):
    """Request model for creating a new user"""
    user_id: str = Field(..., description="Unique user identifier")
    name: str = Field(..., min_length=1, max_length=100, description="User's full name")
    preferred_travel_mode: str = Field(
        default="walking",
        description="Preferred mode of travel (walking/biking/driving)"
    )
    night_travel: bool = Field(
        default=False,
        description="Whether user prefers to travel at night"
    )
    phone: Optional[str] = Field(None, description="User's phone number")
    
    @validator('preferred_travel_mode')
    def validate_travel_mode(cls, v):
        allowed_modes = ['walking', 'biking', 'driving']
        if v.lower() not in allowed_modes:
            raise ValueError(f"Travel mode must be one of: {', '.join(allowed_modes)}")
        return v.lower()


class UserPreferencesUpdate(BaseModel):
    """Request model for updating user preferences"""
    preferred_travel_mode: Optional[str] = Field(None, description="Travel mode")
    night_travel: Optional[bool] = Field(None, description="Night travel preference")
    avoid_high_crime: Optional[bool] = Field(None, description="Avoid high crime areas")
    prefer_well_lit: Optional[bool] = Field(None, description="Prefer well-lit routes")
    prefer_crowded: Optional[bool] = Field(None, description="Prefer crowded areas")
    
    @validator('preferred_travel_mode')
    def validate_travel_mode(cls, v):
        if v is not None:
            allowed_modes = ['walking', 'biking', 'driving']
            if v.lower() not in allowed_modes:
                raise ValueError(f"Travel mode must be one of: {', '.join(allowed_modes)}")
            return v.lower()
        return v


class EmergencyContactRequest(BaseModel):
    """Request model for adding emergency contact"""
    contact_name: str = Field(..., min_length=1, max_length=100, description="Contact name")
    phone_number: str = Field(..., description="Contact phone number")
    relationship: Optional[str] = Field(None, description="Relationship to user")


@router.post(
    "/create",
    response_model=Dict,
    summary="Create New User Profile",
    description="Register a new user with basic profile information and preferences"
)
async def create_user(request: UserCreateRequest):
    """
    Create a new user profile.
    
    This endpoint initializes a user account with basic information and
    default safety preferences. The user_id should be unique across the system.
    
    Request Body:
        user_id: Unique identifier for the user
        name: User's full name
        preferred_travel_mode: Default travel mode (walking/biking/driving)
        night_travel: Whether user travels at night frequently
        phone: Optional phone number
    
    Returns:
        200: User created successfully
        400: User already exists or invalid input
        500: Server error
    
    Example:
        POST /user/create
        {
            "user_id": "user_123",
            "name": "John Doe",
            "preferred_travel_mode": "walking",
            "night_travel": false,
            "phone": "+91-9876543210"
        }
        
        Response:
        {
            "success": true,
            "data": {
                "user_id": "user_123",
                "name": "John Doe",
                "preferred_travel_mode": "walking",
                "night_travel": false
            },
            "message": "User profile created successfully"
        }
    """
    try:
        user_id = request.user_id
        
        if user_id in users_db:
            raise HTTPException(
                status_code=400,
                detail=f"User with ID '{user_id}' already exists"
            )
        
        user_data = {
            "user_id": user_id,
            "name": request.name,
            "preferred_travel_mode": request.preferred_travel_mode,
            "night_travel": request.night_travel,
            "phone": request.phone,
            "preferences": {
                "avoid_high_crime": True,
                "prefer_well_lit": True,
                "prefer_crowded": False
            },
            "emergency_contacts": [],
            "created_at": None
        }
        
        users_db[user_id] = user_data
        
        return success_response(
            data={
                "user_id": user_id,
                "name": request.name,
                "preferred_travel_mode": request.preferred_travel_mode,
                "night_travel": request.night_travel
            },
            message="User profile created successfully"
        )
    
    except HTTPException:
        raise
    
    except Exception as e:
        return error_response(
            message=f"Failed to create user: {str(e)}",
            status_code=500
        )


@router.get(
    "/{user_id}",
    response_model=Dict,
    summary="Get User Profile",
    description="Retrieve complete user profile including preferences and emergency contacts"
)
async def get_user(user_id: str):
    """
    Get user profile by user ID.
    
    Returns complete user information including profile data,
    safety preferences, and emergency contacts.
    
    Path Parameters:
        user_id: Unique user identifier
    
    Returns:
        200: User profile data
        404: User not found
        500: Server error
    
    Example:
        GET /user/user_123
        
        Response:
        {
            "success": true,
            "data": {
                "user_id": "user_123",
                "name": "John Doe",
                "preferred_travel_mode": "walking",
                "night_travel": false,
                "phone": "+91-9876543210",
                "preferences": {
                    "avoid_high_crime": true,
                    "prefer_well_lit": true,
                    "prefer_crowded": false
                },
                "emergency_contacts": [
                    {
                        "contact_name": "Jane Doe",
                        "phone_number": "+91-9876543211",
                        "relationship": "spouse"
                    }
                ]
            }
        }
    """
    try:
        if user_id not in users_db:
            raise HTTPException(
                status_code=404,
                detail=f"User '{user_id}' not found"
            )
        
        user_data = users_db[user_id]
        
        return success_response(
            data=user_data,
            message="User profile retrieved successfully"
        )
    
    except HTTPException:
        raise
    
    except Exception as e:
        return error_response(
            message=f"Failed to retrieve user: {str(e)}",
            status_code=500
        )


@router.put(
    "/{user_id}/preferences",
    response_model=Dict,
    summary="Update User Preferences",
    description="Update safety and travel preferences for a user"
)
async def update_user_preferences(user_id: str, request: UserPreferencesUpdate):
    """
    Update user safety preferences.
    
    Allows users to customize their safety preferences which influence
    route recommendations and safety scoring.
    
    Path Parameters:
        user_id: Unique user identifier
    
    Request Body:
        Fields to update (all optional):
        - preferred_travel_mode
        - night_travel
        - avoid_high_crime
        - prefer_well_lit
        - prefer_crowded
    
    Returns:
        200: Preferences updated successfully
        404: User not found
        500: Server error
    
    Example:
        PUT /user/user_123/preferences
        {
            "preferred_travel_mode": "biking",
            "night_travel": true,
            "avoid_high_crime": true,
            "prefer_well_lit": true,
            "prefer_crowded": false
        }
        
        Response:
        {
            "success": true,
            "data": {
                "user_id": "user_123",
                "preferences": {
                    "preferred_travel_mode": "biking",
                    "night_travel": true,
                    "avoid_high_crime": true,
                    "prefer_well_lit": true,
                    "prefer_crowded": false
                }
            },
            "message": "User preferences updated successfully"
        }
    """
    try:
        if user_id not in users_db:
            raise HTTPException(
                status_code=404,
                detail=f"User '{user_id}' not found"
            )
        
        user = users_db[user_id]
        
        if request.preferred_travel_mode is not None:
            user["preferred_travel_mode"] = request.preferred_travel_mode
        
        if request.night_travel is not None:
            user["night_travel"] = request.night_travel
        
        if request.avoid_high_crime is not None:
            user["preferences"]["avoid_high_crime"] = request.avoid_high_crime
        
        if request.prefer_well_lit is not None:
            user["preferences"]["prefer_well_lit"] = request.prefer_well_lit
        
        if request.prefer_crowded is not None:
            user["preferences"]["prefer_crowded"] = request.prefer_crowded
        
        return success_response(
            data={
                "user_id": user_id,
                "preferred_travel_mode": user["preferred_travel_mode"],
                "night_travel": user["night_travel"],
                "preferences": user["preferences"]
            },
            message="User preferences updated successfully"
        )
    
    except HTTPException:
        raise
    
    except Exception as e:
        return error_response(
            message=f"Failed to update preferences: {str(e)}",
            status_code=500
        )


@router.post(
    "/{user_id}/contacts",
    response_model=Dict,
    summary="Add Emergency Contact",
    description="Add an emergency contact to user's profile for SOS alerts"
)
async def add_emergency_contact(user_id: str, request: EmergencyContactRequest):
    """
    Add an emergency contact to user profile.
    
    Emergency contacts will be notified when user triggers SOS alerts
    or when safety concerns are detected during trips.
    
    Path Parameters:
        user_id: Unique user identifier
    
    Request Body:
        contact_name: Name of emergency contact
        phone_number: Contact's phone number
        relationship: Optional relationship (e.g., "spouse", "friend", "parent")
    
    Returns:
        200: Contact added successfully
        404: User not found
        500: Server error
    
    Example:
        POST /user/user_123/contacts
        {
            "contact_name": "Jane Doe",
            "phone_number": "+91-9876543211",
            "relationship": "spouse"
        }
        
        Response:
        {
            "success": true,
            "data": {
                "user_id": "user_123",
                "contacts_count": 1,
                "latest_contact": {
                    "contact_name": "Jane Doe",
                    "phone_number": "+91-9876543211",
                    "relationship": "spouse"
                }
            },
            "message": "Emergency contact added successfully"
        }
    """
    try:
        if user_id not in users_db:
            raise HTTPException(
                status_code=404,
                detail=f"User '{user_id}' not found"
            )
        
        user = users_db[user_id]
        
        contact_data = {
            "contact_name": request.contact_name,
            "phone_number": request.phone_number,
            "relationship": request.relationship
        }
        
        user["emergency_contacts"].append(contact_data)
        
        return success_response(
            data={
                "user_id": user_id,
                "contacts_count": len(user["emergency_contacts"]),
                "latest_contact": contact_data
            },
            message="Emergency contact added successfully"
        )
    
    except HTTPException:
        raise
    
    except Exception as e:
        return error_response(
            message=f"Failed to add emergency contact: {str(e)}",
            status_code=500
        )


@router.get(
    "/{user_id}/contacts",
    response_model=Dict,
    summary="Get Emergency Contacts",
    description="Retrieve all emergency contacts for a user"
)
async def get_emergency_contacts(user_id: str):
    """
    Get all emergency contacts for a user.
    
    Returns the list of emergency contacts that will be notified
    during SOS alerts.
    
    Path Parameters:
        user_id: Unique user identifier
    
    Returns:
        200: List of emergency contacts
        404: User not found
        500: Server error
    
    Example:
        GET /user/user_123/contacts
        
        Response:
        {
            "success": true,
            "data": {
                "user_id": "user_123",
                "emergency_contacts": [
                    {
                        "contact_name": "Jane Doe",
                        "phone_number": "+91-9876543211",
                        "relationship": "spouse"
                    }
                ],
                "count": 1
            }
        }
    """
    try:
        if user_id not in users_db:
            raise HTTPException(
                status_code=404,
                detail=f"User '{user_id}' not found"
            )
        
        user = users_db[user_id]
        
        return success_response(
            data={
                "user_id": user_id,
                "emergency_contacts": user["emergency_contacts"],
                "count": len(user["emergency_contacts"])
            },
            message=f"Retrieved {len(user['emergency_contacts'])} emergency contact(s)"
        )
    
    except HTTPException:
        raise
    
    except Exception as e:
        return error_response(
            message=f"Failed to retrieve contacts: {str(e)}",
            status_code=500
        )


@router.delete(
    "/{user_id}",
    response_model=Dict,
    summary="Delete User Profile",
    description="Delete a user profile and all associated data"
)
async def delete_user(user_id: str):
    """
    Delete a user profile.
    
    Removes the user and all associated data (preferences, contacts, etc.)
    from the system. This action cannot be undone.
    
    Path Parameters:
        user_id: Unique user identifier
    
    Returns:
        200: User deleted successfully
        404: User not found
        500: Server error
    
    Example:
        DELETE /user/user_123
        
        Response:
        {
            "success": true,
            "data": {
                "user_id": "user_123",
                "deleted": true
            },
            "message": "User profile deleted successfully"
        }
    """
    try:
        if user_id not in users_db:
            raise HTTPException(
                status_code=404,
                detail=f"User '{user_id}' not found"
            )
        
        del users_db[user_id]
        
        return success_response(
            data={
                "user_id": user_id,
                "deleted": True
            },
            message="User profile deleted successfully"
        )
    
    except HTTPException:
        raise
    
    except Exception as e:
        return error_response(
            message=f"Failed to delete user: {str(e)}",
            status_code=500
        )