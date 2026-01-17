from fastapi import APIRouter, Query, HTTPException
from typing import Optional, List
from pydantic import BaseModel

from app.services.geocoding_service import geocoding_service

router = APIRouter(prefix="/geocoding", tags=["Geocoding"])


class GeocodeRequest(BaseModel):
    address: str


class GeocodeResponse(BaseModel):
    success: bool
    address: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class ReverseGeocodeResponse(BaseModel):
    success: bool
    address: Optional[str] = None
    components: Optional[dict] = None


class PlaceSearchResponse(BaseModel):
    success: bool
    results: List[dict]


@router.post("/geocode", response_model=GeocodeResponse)
async def geocode(request: GeocodeRequest):
    """
    Convert address to coordinates.
    """
    result = geocoding_service.geocode_address(request.address)
    
    if result:
        return GeocodeResponse(
            success=True,
            address=result["address"],
            latitude=result["latitude"],
            longitude=result["longitude"]
        )
    
    raise HTTPException(status_code=404, detail="Address not found")


@router.get("/reverse", response_model=ReverseGeocodeResponse)
async def reverse_geocode(
    lat: float = Query(..., description="Latitude"),
    lon: float = Query(..., description="Longitude")
):
    """
    Convert coordinates to address.
    """
    result = geocoding_service.reverse_geocode(lat, lon)
    
    if result:
        return ReverseGeocodeResponse(
            success=True,
            address=result["address"],
            components=result.get("components")
        )
    
    raise HTTPException(status_code=404, detail="Location not found")


@router.get("/search", response_model=PlaceSearchResponse)
async def search_places(
    query: str = Query(..., min_length=2, description="Search query"),
    limit: int = Query(5, ge=1, le=20)
):
    """
    Search for places by name.
    """
    results = geocoding_service.search_places(query, limit)
    
    return PlaceSearchResponse(
        success=True,
        results=results
    )