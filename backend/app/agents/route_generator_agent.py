from typing import Dict, Any, List, Optional
from datetime import datetime
import math

from app.ai.orchestrator import AIOrchestrator


class RouteGeneratorAgent:
    def __init__(self, ai_orchestrator: Optional[AIOrchestrator] = None):
        self.ai_orchestrator = ai_orchestrator
    
    
    def plan_safe_route(
        self,
        start_lat: float,
        start_lon: float,
        end_lat: float,
        end_lon: float,
        user_preferences: Optional[Dict[str, Any]] = None,
        travel_time: Optional[datetime] = None,
        community_reports: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Main entry point for route planning with safety analysis.
        """
        user_prefs = user_preferences or {}
        check_time = travel_time or datetime.utcnow()
        
        routes = self._generate_routes(start_lat, start_lon, end_lat, end_lon)
        
        if not routes:
            return {
                "success": False,
                "message": "No routes found",
                "routes": []
            }
        
        analyzed_routes = []
        
        for idx, route in enumerate(routes):
            route_points = route.get("route_points", [])
            
            nearby_reports = []
            if community_reports:
                for point in route_points:
                    point_reports = self._filter_reports_by_proximity(
                        community_reports,
                        point["latitude"],
                        point["longitude"],
                        radius_km=0.5
                    )
                    nearby_reports.extend(point_reports)
                
                nearby_reports = list({r["id"]: r for r in nearby_reports}.values())
            
            safety_analysis = self._calculate_route_risk(
                route_points=[(p["latitude"], p["longitude"]) for p in route_points],
                all_reports=nearby_reports,
                radius_km=0.5,
                travel_time=check_time
            )
            
            ai_assessment = None
            if self.ai_orchestrator and user_prefs.get("enable_ai_analysis", True):
                try:
                    ai_assessment = self.ai_orchestrator.score_route_safety(
                        route_data={
                            "distance_km": route.get("distance_km"),
                            "duration_minutes": route.get("duration_minutes"),
                            "route_type": route.get("route_type")
                        },
                        reports=nearby_reports,
                        time_of_day="night" if safety_analysis.get("is_night_time") else "day",
                        user_preferences=user_prefs
                    )
                except Exception as e:
                    print(f"AI assessment failed: {e}")
            
            analyzed_routes.append({
                "route_index": idx,
                "route_name": route.get("route_name", f"Route {idx + 1}"),
                "distance_km": route.get("distance_km"),
                "duration_minutes": route.get("duration_minutes"),
                "route_type": route.get("route_type"),
                "route_points": route_points,
                "safety_score": safety_analysis.get("overall_risk_score", 50),
                "risk_label": safety_analysis.get("risk_label", "moderate"),
                "risky_segments": safety_analysis.get("risky_segments", []),
                "report_count": len(nearby_reports),
                "requires_warning": safety_analysis.get("overall_risk_score", 50) >= 50,
                "ai_assessment": ai_assessment,
                "time_context": "night" if safety_analysis.get("is_night_time") else "day"
            })
        
        analyzed_routes.sort(key=lambda r: r["safety_score"])
        
        recommended_route = analyzed_routes[0]
        
        explanation = None
        if self.ai_orchestrator and len(analyzed_routes) > 1:
            try:
                explanation = self.ai_orchestrator.explain_route_choice(
                    chosen_route=recommended_route,
                    alternative_routes=analyzed_routes[1:3],
                    decision_factors={
                        "safety_priority": user_prefs.get("safety_priority", "balanced"),
                        "time_of_day": "night" if check_time.hour >= 20 or check_time.hour < 6 else "day",
                        "total_reports": recommended_route["report_count"]
                    }
                )
            except Exception as e:
                print(f"Explanation generation failed: {e}")
        
        return {
            "success": True,
            "recommended_route_index": 0,
            "explanation": explanation,
            "routes": analyzed_routes,
            "total_routes": len(analyzed_routes),
            "timestamp": datetime.utcnow().isoformat()
        }
    
    
    def get_route_alternatives(
        self,
        current_route_id: str,
        current_location: Dict[str, float],
        destination: Dict[str, float],
        avoid_areas: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Generate alternative routes avoiding specific areas.
        """
        routes = self._generate_routes(
            current_location["latitude"],
            current_location["longitude"],
            destination["latitude"],
            destination["longitude"]
        )
        
        if avoid_areas:
            filtered_routes = []
            for route in routes:
                has_conflict = False
                for point in route.get("route_points", []):
                    for avoid in avoid_areas:
                        distance = self._calculate_distance(
                            point["latitude"], point["longitude"],
                            avoid["latitude"], avoid["longitude"]
                        )
                        if distance < avoid.get("radius_km", 0.5):
                            has_conflict = True
                            break
                    if has_conflict:
                        break
                
                if not has_conflict:
                    filtered_routes.append(route)
            
            routes = filtered_routes
        
        return {
            "success": True,
            "alternative_routes": routes,
            "count": len(routes)
        }
    
    
    def _generate_routes(
        self,
        start_lat: float,
        start_lon: float,
        end_lat: float,
        end_lon: float,
        alternatives: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Generate multiple route alternatives between two points.
        Mock implementation for demo.
        """
        import random
        
        routes = []
        base_distance = self._calculate_distance(start_lat, start_lon, end_lat, end_lon)
        route_types = ["fastest", "balanced", "safest"]
        
        for i in range(min(alternatives, 3)):
            route_points = self._generate_route_points(start_lat, start_lon, end_lat, end_lon, segments=8 + i * 2)
            distance_km = base_distance * (1 + i * 0.15)
            duration_minutes = (distance_km / 40) * 60
            
            routes.append({
                "route_id": f"route_{i}",
                "route_name": f"{route_types[i].capitalize()} Route",
                "route_type": route_types[i],
                "distance_km": round(distance_km, 2),
                "duration_minutes": round(duration_minutes, 1),
                "route_points": route_points,
                "polyline": f"polyline_{len(route_points)}_points"
            })
        
        return routes
    
    
    def _generate_route_points(
        self,
        start_lat: float,
        start_lon: float,
        end_lat: float,
        end_lon: float,
        segments: int = 10
    ) -> List[Dict[str, float]]:
        """
        Generate intermediate points along a route.
        """
        import random
        
        points = []
        for i in range(segments + 1):
            fraction = i / segments
            lat = start_lat + (end_lat - start_lat) * fraction
            lon = start_lon + (end_lon - start_lon) * fraction
            noise_lat = random.uniform(-0.001, 0.001)
            noise_lon = random.uniform(-0.001, 0.001)
            
            points.append({
                "latitude": lat + noise_lat,
                "longitude": lon + noise_lon,
                "sequence": i
            })
        
        return points
    
    
    def _filter_reports_by_proximity(
        self,
        reports: List[Dict[str, Any]],
        lat: float,
        lon: float,
        radius_km: float = 0.5
    ) -> List[Dict[str, Any]]:
        """
        Filter reports within a given radius of a location.
        """
        nearby = []
        for report in reports:
            report_lat = report.get("latitude", 0)
            report_lon = report.get("longitude", 0)
            distance = self._calculate_distance(lat, lon, report_lat, report_lon)
            
            if distance <= radius_km:
                nearby.append(report)
        
        return nearby
    
    
    def _calculate_route_risk(
        self,
        route_points: List[tuple],
        all_reports: List[Dict[str, Any]],
        radius_km: float = 0.5,
        travel_time: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Calculate overall risk score for a route based on reports.
        """
        if not route_points:
            return {
                "overall_risk_score": 0,
                "risk_label": "safe",
                "is_night_time": False,
                "risky_segments": []
            }
        
        check_time = travel_time or datetime.utcnow()
        is_night = check_time.hour >= 20 or check_time.hour < 6
        
        total_risk = 0
        risky_segments = []
        
        for idx, point in enumerate(route_points):
            lat, lon = point
            nearby_reports = self._filter_reports_by_proximity(
                all_reports,
                lat,
                lon,
                radius_km
            )
            
            segment_risk = len(nearby_reports) * 10
            if is_night:
                segment_risk *= 1.5
            
            total_risk += segment_risk
            
            if segment_risk > 20:
                risky_segments.append({
                    "segment_index": idx,
                    "latitude": lat,
                    "longitude": lon,
                    "risk_score": segment_risk,
                    "report_count": len(nearby_reports)
                })
        
        avg_risk = total_risk / len(route_points) if route_points else 0
        
        if avg_risk < 10:
            risk_label = "safe"
        elif avg_risk < 30:
            risk_label = "low"
        elif avg_risk < 50:
            risk_label = "moderate"
        elif avg_risk < 70:
            risk_label = "high"
        else:
            risk_label = "critical"
        
        return {
            "overall_risk_score": min(avg_risk, 100),
            "risk_label": risk_label,
            "is_night_time": is_night,
            "risky_segments": risky_segments
        }
    
    
    def _calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        Calculate distance between two coordinates using Haversine formula.
        Returns distance in kilometers.
        """
        R = 6371.0
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)
        a = math.sin(delta_lat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2)**2
        c = 2 * math.asin(math.sqrt(a))
        return R * c