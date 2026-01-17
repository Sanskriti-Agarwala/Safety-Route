import json
import math
import os
from typing import List, Dict, Optional
from datetime import datetime


class SafetyScoreService:
    """Service for calculating route safety scores"""
    
    def __init__(self):
        self.crime_zones = self._load_crime_zones()
        self.crowd_data = self._load_crowd_data()
    
    def _load_crime_zones(self) -> List[Dict]:
        """Load crime zones from JSON file"""
        try:
            file_path = os.path.join(os.path.dirname(__file__), '../data/mock_crime_zones.json')
            with open(file_path, 'r') as f:
                data = json.load(f)
                return data.get('zones', [])
        except Exception as e:
            print(f"Warning: Could not load crime zones: {e}")
            return []
    
    def _load_crowd_data(self) -> List[Dict]:
        """Load crowd data from JSON file"""
        try:
            file_path = os.path.join(os.path.dirname(__file__), '../data/mock_crowd_data.json')
            with open(file_path, 'r') as f:
                data = json.load(f)
                return data.get('areas', [])
        except Exception as e:
            print(f"Warning: Could not load crowd data: {e}")
            return []
    
    async def calculate_safety_score(
        self,
        route: Dict,
        time_of_day: int = 12,
        user_profile: Optional[Dict] = None
    ) -> Dict:
        """
        Calculate comprehensive safety score for a route.
        
        Returns dict with:
        - overall_score: 0-100 (higher is safer)
        - crime_score: 0-100
        - lighting_score: 0-100
        - crowd_score: 0-100
        - time_factor: 0-1 multiplier
        """
        waypoints = route.get('waypoints', [])
        
        if not waypoints:
            return self._default_score()
        
        # Calculate individual scores
        crime_score = self._calculate_crime_score(waypoints)
        lighting_score = self._calculate_lighting_score(waypoints, time_of_day)
        crowd_score = self._calculate_crowd_score(waypoints, time_of_day)
        
        # Time factor (night is less safe)
        time_factor = self._get_time_factor(time_of_day)
        
        # Calculate weighted overall score
        overall_score = (
            crime_score * 0.4 +      # Crime is most important (40%)
            lighting_score * 0.3 +    # Lighting is important (30%)
            crowd_score * 0.3         # Crowd density (30%)
        ) * time_factor
        
        return {
            "overall_score": round(overall_score, 2),
            "crime_score": round(crime_score, 2),
            "lighting_score": round(lighting_score, 2),
            "crowd_score": round(crowd_score, 2),
            "time_factor": round(time_factor, 2)
        }
    
    def _calculate_crime_score(self, waypoints: List[Dict]) -> float:
        """
        Calculate crime safety score based on proximity to crime zones.
        Returns 0-100 (100 = safest)
        """
        if not self.crime_zones:
            return 85.0  # Default safe score if no data
        
        total_danger = 0
        danger_points = 0
        
        for point in waypoints:
            for zone in self.crime_zones:
                if zone['type'] in ['high_crime', 'medium_crime']:
                    distance = self._calculate_distance(
                        point['lat'], point['lng'],
                        zone['center']['lat'], zone['center']['lng']
                    )
                    
                    # Check if point is within danger zone
                    if distance < zone['radius'] / 1000:  # radius in meters, distance in km
                        severity_penalty = {
                            'high': 50,
                            'medium': 25,
                            'low': 10
                        }.get(zone['severity'], 10)
                        
                        # Closer = more dangerous
                        proximity_factor = 1 - (distance / (zone['radius'] / 1000))
                        total_danger += severity_penalty * proximity_factor
                        danger_points += 1
        
        if danger_points == 0:
            return 95.0  # No crime zones nearby
        
        # Convert danger to safety score
        avg_danger = total_danger / len(waypoints)
        safety_score = max(0, 100 - avg_danger)
        
        return safety_score
    
    def _calculate_lighting_score(self, waypoints: List[Dict], time_of_day: int) -> float:
        """
        Calculate lighting safety score.
        Returns 0-100 (100 = well lit)
        """
        # During day, lighting doesn't matter much
        if 6 <= time_of_day <= 18:
            return 95.0
        
        # Night time - check for poorly lit zones
        total_darkness = 0
        dark_points = 0
        
        for point in waypoints:
            for zone in self.crime_zones:
                if zone['type'] == 'poor_lighting':
                    distance = self._calculate_distance(
                        point['lat'], point['lng'],
                        zone['center']['lat'], zone['center']['lng']
                    )
                    
                    if distance < zone['radius'] / 1000:
                        proximity_factor = 1 - (distance / (zone['radius'] / 1000))
                        total_darkness += 40 * proximity_factor
                        dark_points += 1
        
        if dark_points == 0:
            return 80.0  # Assume moderate lighting at night
        
        avg_darkness = total_darkness / len(waypoints)
        lighting_score = max(20, 100 - avg_darkness)
        
        return lighting_score
    
    def _calculate_crowd_score(self, waypoints: List[Dict], time_of_day: int) -> float:
        """
        Calculate crowd density score.
        Returns 0-100 (moderate crowd = safest ~70-80)
        """
        if not self.crowd_data:
            return 70.0  # Default moderate crowd
        
        crowd_levels = []
        
        for point in waypoints:
            for area in self.crowd_data:
                distance = self._calculate_distance(
                    point['lat'], point['lng'],
                    area['location']['lat'], area['location']['lng']
                )
                
                if distance < area['radius'] / 1000:
                    # Get crowd level for time of day
                    time_period = self._get_time_period(time_of_day)
                    crowd_level = area['time_pattern'].get(time_period, 'medium')
                    
                    # Convert to score (moderate is best for safety)
                    crowd_score_map = {
                        'very_high': 60,  # Too crowded
                        'high': 75,       # Good
                        'medium': 80,     # Best
                        'low': 65,        # A bit isolated
                        'very_low': 45    # Too isolated
                    }
                    crowd_levels.append(crowd_score_map.get(crowd_level, 70))
        
        if not crowd_levels:
            return 70.0
        
        return sum(crowd_levels) / len(crowd_levels)
    
    def _get_time_factor(self, time_of_day: int) -> float:
        """
        Get time-based safety multiplier.
        Returns 0-1 (1 = safest time)
        """
        if 6 <= time_of_day <= 18:
            return 1.0  # Daytime - safest
        elif 19 <= time_of_day <= 21:
            return 0.85  # Early evening - pretty safe
        elif 22 <= time_of_day <= 23 or 0 <= time_of_day <= 5:
            return 0.6  # Night - less safe
        else:
            return 0.7
    
    def _get_time_period(self, time_of_day: int) -> str:
        """Convert hour to time period"""
        if 6 <= time_of_day <= 11:
            return 'morning'
        elif 12 <= time_of_day <= 17:
            return 'afternoon'
        elif 18 <= time_of_day <= 21:
            return 'evening'
        else:
            return 'night'
    
    async def get_unsafe_zones(self, route: Dict) -> List[Dict]:
        """
        Get list of unsafe zones along the route.
        """
        waypoints = route.get('waypoints', [])
        unsafe_zones = []
        
        for point in waypoints:
            for zone in self.crime_zones:
                distance = self._calculate_distance(
                    point['lat'], point['lng'],
                    zone['center']['lat'], zone['center']['lng']
                )
                
                if distance < zone['radius'] / 1000:
                    # Calculate distance from route start
                    distance_from_start = self._calculate_distance(
                        waypoints[0]['lat'], waypoints[0]['lng'],
                        point['lat'], point['lng']
                    ) * 1000  # to meters
                    
                    unsafe_zone = {
                        "zone_id": zone['id'],
                        "type": zone['type'],
                        "severity": zone['severity'],
                        "location": zone['center'],
                        "description": zone['description'],
                        "distance_from_start": round(distance_from_start, 2)
                    }
                    
                    # Avoid duplicates
                    if not any(uz['zone_id'] == zone['id'] for uz in unsafe_zones):
                        unsafe_zones.append(unsafe_zone)
        
        return unsafe_zones
    
    async def check_segment_safety(self, point1: Dict, point2: Dict) -> List[str]:
        """
        Check safety of a route segment.
        Returns list of warning messages.
        """
        warnings = []
        
        # Check if segment passes through unsafe zones
        for zone in self.crime_zones:
            # Check both endpoints
            dist1 = self._calculate_distance(
                point1['lat'], point1['lng'],
                zone['center']['lat'], zone['center']['lng']
            )
            dist2 = self._calculate_distance(
                point2['lat'], point2['lng'],
                zone['center']['lat'], zone['center']['lng']
            )
            
            threshold = zone['radius'] / 1000
            
            if dist1 < threshold or dist2 < threshold:
                if zone['severity'] == 'high':
                    warnings.append(f"⚠️ HIGH RISK: {zone['description']}")
                elif zone['severity'] == 'medium':
                    warnings.append(f"⚡ CAUTION: {zone['description']}")
        
        return warnings
    
    def _calculate_distance(self, lat1: float, lng1: float, lat2: float, lng2: float) -> float:
        """Calculate distance between two points in kilometers"""
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
    
    def _default_score(self) -> Dict:
        """Return default safety score"""
        return {
            "overall_score": 75.0,
            "crime_score": 80.0,
            "lighting_score": 75.0,
            "crowd_score": 70.0,
            "time_factor": 1.0
        }