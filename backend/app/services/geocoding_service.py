from typing import Dict, Any, Optional, List
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError


class GeocodingService:
    def __init__(self):
        self.geolocator = Nominatim(user_agent="safety_route_app")
        self.cache = {}
    
    def geocode_address(self, address: str) -> Optional[Dict[str, Any]]:
        """Convert address to coordinates"""
        if address in self.cache:
            return self.cache[address]
        
        try:
            location = self.geolocator.geocode(address, timeout=10)
            
            if location:
                result = {
                    "address": location.address,
                    "latitude": location.latitude,
                    "longitude": location.longitude,
                    "raw": location.raw
                }
                self.cache[address] = result
                return result
            
            return None
        
        except (GeocoderTimedOut, GeocoderServiceError) as e:
            print(f"Geocoding error: {e}")
            return None
    
    def reverse_geocode(self, latitude: float, longitude: float) -> Optional[Dict[str, Any]]:
        """Convert coordinates to address"""
        cache_key = f"{latitude},{longitude}"
        
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        try:
            location = self.geolocator.reverse(
                f"{latitude}, {longitude}",
                timeout=10,
                language='en'
            )
            
            if location:
                result = {
                    "address": location.address,
                    "latitude": latitude,
                    "longitude": longitude,
                    "components": location.raw.get('address', {})
                }
                self.cache[cache_key] = result
                return result
            
            return None
        
        except (GeocoderTimedOut, GeocoderServiceError) as e:
            print(f"Reverse geocoding error: {e}")
            return None
    
    def search_places(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Search for places"""
        try:
            locations = self.geolocator.geocode(
                query,
                exactly_one=False,
                limit=limit,
                timeout=10
            )
            
            if not locations:
                return []
            
            results = []
            for location in locations:
                results.append({
                    "name": location.address,
                    "latitude": location.latitude,
                    "longitude": location.longitude,
                    "display_name": location.address
                })
            
            return results
        
        except (GeocoderTimedOut, GeocoderServiceError) as e:
            print(f"Search error: {e}")
            return []


# Singleton instance
geocoding_service = GeocodingService()