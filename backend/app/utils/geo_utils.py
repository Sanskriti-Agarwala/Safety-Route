from geopy.geocoders import Nominatim
from geopy.distance import geodesic
from typing import Optional, Tuple, Dict
import time

# Initialize geocoder
geolocator = Nominatim(user_agent="safety-route-navigator")


def geocode_address(address: str) -> Optional[Dict[str, float]]:
    """
    Convert address to latitude/longitude.
    Returns: {"latitude": float, "longitude": float} or None
    """
    try:
        location = geolocator.geocode(address, timeout=10)
        if location:
            return {
                "latitude": location.latitude,
                "longitude": location.longitude,
                "display_name": location.address
            }
        return None
    except Exception as e:
        print(f"Geocoding error: {e}")
        return None


def reverse_geocode(lat: float, lon: float) -> Optional[str]:
    """
    Convert latitude/longitude to address.
    """
    try:
        location = geolocator.reverse(f"{lat}, {lon}", timeout=10)
        if location:
            return location.address
        return None
    except Exception as e:
        print(f"Reverse geocoding error: {e}")
        return None


def calculate_distance(
    lat1: float, lon1: float, 
    lat2: float, lon2: float
) -> float:
    """
    Calculate distance between two points in kilometers.
    """
    point1 = (lat1, lon1)
    point2 = (lat2, lon2)
    return geodesic(point1, point2).kilometers


def get_bounding_box(
    center_lat: float, 
    center_lon: float, 
    radius_km: float = 5
) -> Dict[str, float]:
    """
    Get bounding box coordinates for a radius around a center point.
    Returns: {"north": float, "south": float, "east": float, "west": float}
    """
    # Approximate degrees per km
    lat_offset = radius_km / 111.0
    lon_offset = radius_km / (111.0 * abs(geodesic((center_lat, 0), (center_lat, 1)).km))
    
    return {
        "north": center_lat + lat_offset,
        "south": center_lat - lat_offset,
        "east": center_lon + lon_offset,
        "west": center_lon - lon_offset
    }