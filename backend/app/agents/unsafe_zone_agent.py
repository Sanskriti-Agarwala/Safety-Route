from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import math

from app.services.safety_score_service import calculate_report_risk, haversine_distance


class UnsafeZoneAgent:
    def __init__(self):
        self.danger_threshold = 70
        self.warning_threshold = 50
    
    
    def identify_unsafe_zones(
        self,
        reports: List[Dict[str, Any]],
        area_bounds: Optional[Dict[str, float]] = None,
        grid_size_km: float = 0.5
    ) -> Dict[str, Any]:
        """
        Identify geographic zones with high safety risks.
        """
        if not reports:
            return {
                "unsafe_zones": [],
                "warning_zones": [],
                "total_zones_analyzed": 0
            }
        
        zone_clusters = self._cluster_reports(reports, radius_km=grid_size_km)
        
        unsafe_zones = []
        warning_zones = []
        
        for cluster_id, cluster_reports in zone_clusters.items():
            center_lat, center_lon = self._calculate_cluster_center(cluster_reports)
            
            zone_risk = calculate_report_risk(cluster_reports)
            
            zone_info = {
                "zone_id": f"zone_{cluster_id}",
                "center_latitude": center_lat,
                "center_longitude": center_lon,
                "radius_km": grid_size_km,
                "risk_score": zone_risk["risk_score"],
                "risk_label": zone_risk["risk_label"],
                "report_count": len(cluster_reports),
                "critical_reports": sum(1 for r in cluster_reports if r.get("severity", 1) >= 4),
                "dominant_threats": zone_risk.get("dominant_categories", []),
                "identified_at": datetime.utcnow().isoformat()
            }
            
            if zone_risk["risk_score"] >= self.danger_threshold:
                unsafe_zones.append(zone_info)
            elif zone_risk["risk_score"] >= self.warning_threshold:
                warning_zones.append(zone_info)
        
        return {
            "unsafe_zones": sorted(unsafe_zones, key=lambda z: z["risk_score"], reverse=True),
            "warning_zones": sorted(warning_zones, key=lambda z: z["risk_score"], reverse=True),
            "total_zones_analyzed": len(zone_clusters),
            "total_reports_processed": len(reports),
            "analysis_timestamp": datetime.utcnow().isoformat()
        }
    
    
    def check_route_through_unsafe_zones(
        self,
        route_points: List[Tuple[float, float]],
        unsafe_zones: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Check if a route passes through identified unsafe zones.
        """
        conflicts = []
        
        for idx, (lat, lon) in enumerate(route_points):
            for zone in unsafe_zones:
                distance = haversine_distance(
                    lat, lon,
                    zone["center_latitude"],
                    zone["center_longitude"]
                )
                
                if distance <= zone["radius_km"]:
                    conflicts.append({
                        "segment_index": idx,
                        "zone_id": zone["zone_id"],
                        "zone_risk_score": zone["risk_score"],
                        "distance_from_zone_center_km": round(distance, 2),
                        "dominant_threats": zone.get("dominant_threats", [])
                    })
        
        return {
            "passes_through_unsafe_zones": len(conflicts) > 0,
            "conflict_count": len(conflicts),
            "conflicts": conflicts,
            "max_risk_encountered": max((c["zone_risk_score"] for c in conflicts), default=0),
            "recommendation": "avoid_route" if len(conflicts) > 2 else "proceed_with_caution" if conflicts else "safe"
        }
    
    
    def suggest_zone_avoidance(
        self,
        start: Tuple[float, float],
        end: Tuple[float, float],
        unsafe_zones: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Suggest areas to avoid when planning routes.
        """
        avoidance_list = []
        
        for zone in unsafe_zones:
            if zone["risk_score"] >= self.danger_threshold:
                avoidance_list.append({
                    "latitude": zone["center_latitude"],
                    "longitude": zone["center_longitude"],
                    "radius_km": zone["radius_km"] * 1.5,
                    "reason": f"High risk zone: {', '.join(zone.get('dominant_threats', ['multiple threats']))}",
                    "risk_score": zone["risk_score"],
                    "priority": "high"
                })
        
        return sorted(avoidance_list, key=lambda a: a["risk_score"], reverse=True)
    
    
    def _cluster_reports(self, reports: List[Dict[str, Any]], radius_km: float) -> Dict[int, List[Dict[str, Any]]]:
        """Simple clustering of reports by proximity"""
        clusters = {}
        cluster_id = 0
        assigned = set()
        
        for i, report in enumerate(reports):
            if i in assigned:
                continue
            
            cluster = [report]
            assigned.add(i)
            
            for j, other_report in enumerate(reports):
                if j in assigned or i == j:
                    continue
                
                distance = haversine_distance(
                    report.get("latitude", 0),
                    report.get("longitude", 0),
                    other_report.get("latitude", 0),
                    other_report.get("longitude", 0)
                )
                
                if distance <= radius_km:
                    cluster.append(other_report)
                    assigned.add(j)
            
            if len(cluster) >= 2:
                clusters[cluster_id] = cluster
                cluster_id += 1
        
        return clusters
    
    
    def _calculate_cluster_center(self, reports: List[Dict[str, Any]]) -> Tuple[float, float]:
        """Calculate geographic center of report cluster"""
        if not reports:
            return (0.0, 0.0)
        
        avg_lat = sum(r.get("latitude", 0) for r in reports) / len(reports)
        avg_lon = sum(r.get("longitude", 0) for r in reports) / len(reports)
        
        return (avg_lat, avg_lon)