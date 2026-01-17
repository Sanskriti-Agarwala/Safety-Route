import json
import math
from typing import List, Dict, Optional
import random


class MapsService:
    """Service for route generation and map operations"""
    
    def __init__(self):
        self.mock_mode = True  # Set to False when using real API
    
    async def get_routes(
        self, 
        source: Dict, 
        destination: Dict, 
        mode: str = "walking",
        alternatives: bool = True,
        max_routes: int = 3
    ) -> List[Dict]:
        """
        Get routes from source to destination.
        Returns mock routes for demo purposes.
        """
        if self.mock_mode:
            return self._generate_mock_routes(source, destination, max_routes)
        else:
            # TODO: Implement real API call
            pass
    
    def _generate_mock_routes(
        self, 
        source: Dict, 
        destination: Dict, 
        num_routes: int = 3
    ) -> List[Dict]:
        """Generate mock routes for testing"""
        
        routes = []
        base_distance = self._calculate_distance(
            source['lat'], source['lng'],
            destination['lat'], destination['lng']
        )
        
        for i in range(num_routes):
            # Generate slightly different routes
            distance_variation = random.uniform(0.9, 1.3)
            distance = base_distance * distance_variation * 1000  # to meters
            duration = distance / 1.4 * 60  # walking speed ~1.4 m/s
            
            # Generate waypoints for the route
            waypoints = self._generate_waypoints(
                source, destination, points=8 + i * 2
            )
            
            route = {
                "summary": f"Route {i + 1} via {'Main Road' if i == 0 else 'Alternative Path'}",
                "distance": round(distance, 2),
                "duration": round(duration, 2),
                "polyline": self._encode_polyline(waypoints),
                "waypoints": waypoints,
                "bounds": {
                    "northeast": {
                        "lat": max(source['lat'], destination['lat']) + 0.001,
                        "lng": max(source['lng'], destination['lng']) + 0.001
                    },
                    "southwest": {
                        "lat": min(source['lat'], destination['lat']) - 0.001,
                        "lng": min(source['lng'], destination['lng']) - 0.001
                    }
                }
            }
            routes.append(route)
        
        return routes
    
    def _generate_waypoints(
        self, 
        source: Dict, 
        destination: Dict, 
        points: int = 10
    ) -> List[Dict]:
        """Generate intermediate waypoints between source and destination"""
        waypoints = []
        
        for i in range(points + 1):
            t = i / points
            # Linear interpolation with slight random variation
            lat = source['lat'] + (destination['lat'] - source['lat']) * t
            lng = source['lng'] + (destination['lng'] - source['lng']) * t
            
            # Add some curve to make it look more realistic
            if i > 0 and i < points:
                lat += random.uniform(-0.0005, 0.0005)
                lng += random.uniform(-0.0005, 0.0005)
            
            waypoints.append({"lat": lat, "lng": lng})
        
        return waypoints
    
    def _calculate_distance(
        self, 
        lat1: float, 
        lng1: float, 
        lat2: float, 
        lng2: float
    ) -> float:
        """Calculate distance between two points in kilometers (Haversine formula)"""
        R = 6371  # Earth's radius in km
        
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lng = math.radians(lng2 - lng1)
        
        a = (math.sin(delta_lat / 2) ** 2 +
             math.cos(lat1_rad) * math.cos(lat2_rad) *
             math.sin(delta_lng / 2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        return R * c
    
    def _encode_polyline(self, waypoints: List[Dict]) -> str:
        """Simple polyline encoding (mock version)"""
        # For demo, just return a simple encoded string
        return f"encoded_{len(waypoints)}_points"
    
    def decode_polyline(self, polyline: str) -> List[Dict]:
        """Decode polyline to list of coordinates"""
        # Mock implementation
        return []