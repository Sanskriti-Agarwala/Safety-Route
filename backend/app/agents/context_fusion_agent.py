from typing import Dict, Any, List, Optional
from datetime import datetime
from collections import defaultdict


class ContextFusionAgent:
    def __init__(self):
        self.data_sources = []
    
    
    def fuse_safety_signals(
        self,
        community_reports: List[Dict[str, Any]],
        crime_zones: Optional[List[Dict[str, Any]]] = None,
        crowd_data: Optional[Dict[str, Any]] = None,
        poi_data: Optional[List[Dict[str, Any]]] = None,
        time_context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Combine multiple data sources into unified safety intelligence.
        """
        fused_data = {
            "total_signals": 0,
            "signal_sources": [],
            "confidence_score": 0.0,
            "threat_categories": defaultdict(int),
            "safety_factors": []
        }
        
        if community_reports:
            fused_data["total_signals"] += len(community_reports)
            fused_data["signal_sources"].append("community_reports")
            
            for report in community_reports:
                category = report.get("category", "other")
                fused_data["threat_categories"][category] += 1
            
            recent_reports = [r for r in community_reports 
                            if self._is_recent(r.get("timestamp"), hours=24)]
            
            if len(recent_reports) > 0:
                fused_data["safety_factors"].append({
                    "source": "community_reports",
                    "factor": "recent_incidents",
                    "count": len(recent_reports),
                    "weight": 0.4
                })
        
        if crime_zones:
            fused_data["total_signals"] += len(crime_zones)
            fused_data["signal_sources"].append("crime_zones")
            fused_data["safety_factors"].append({
                "source": "crime_zones",
                "factor": "high_crime_areas",
                "count": len(crime_zones),
                "weight": 0.3
            })
        
        if crowd_data:
            fused_data["signal_sources"].append("crowd_data")
            crowd_level = crowd_data.get("crowd_level", "unknown")
            
            if crowd_level in ["high", "very_high"]:
                fused_data["safety_factors"].append({
                    "source": "crowd_data",
                    "factor": "high_foot_traffic",
                    "level": crowd_level,
                    "weight": 0.15,
                    "impact": "positive"
                })
        
        if poi_data:
            fused_data["signal_sources"].append("poi_data")
            safety_pois = [p for p in poi_data 
                          if p.get("type") in ["police_station", "hospital", "fire_station"]]
            
            if safety_pois:
                fused_data["safety_factors"].append({
                    "source": "poi_data",
                    "factor": "safety_infrastructure",
                    "count": len(safety_pois),
                    "weight": 0.15,
                    "impact": "positive"
                })
        
        if time_context == "night":
            fused_data["safety_factors"].append({
                "source": "time_context",
                "factor": "night_time",
                "weight": 0.2,
                "impact": "negative"
            })
        
        total_weight = sum(f.get("weight", 0) for f in fused_data["safety_factors"])
        fused_data["confidence_score"] = min(total_weight, 1.0)
        
        fused_data["threat_categories"] = dict(fused_data["threat_categories"])
        
        return fused_data
    
    
    def enrich_route_context(
        self,
        route: Dict[str, Any],
        external_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Enrich route with contextual safety information.
        """
        enriched = {
            **route,
            "context": {
                "data_sources": [],
                "enrichment_timestamp": datetime.utcnow().isoformat()
            }
        }
        
        if "weather" in external_data:
            enriched["context"]["weather"] = external_data["weather"]
            enriched["context"]["data_sources"].append("weather")
        
        if "traffic" in external_data:
            enriched["context"]["traffic_level"] = external_data["traffic"]
            enriched["context"]["data_sources"].append("traffic")
        
        if "events" in external_data:
            enriched["context"]["nearby_events"] = external_data["events"]
            enriched["context"]["data_sources"].append("events")
        
        return enriched
    
    
    def _is_recent(self, timestamp_str: Optional[str], hours: int = 24) -> bool:
        """Check if timestamp is within last N hours"""
        if not timestamp_str:
            return False
        
        try:
            timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
            age = (datetime.utcnow() - timestamp).total_seconds() / 3600
            return age <= hours
        except:
            return False