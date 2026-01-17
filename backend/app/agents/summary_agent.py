from typing import Dict, Any, List, Optional
from datetime import datetime

from app.ai.orchestrator import AIOrchestrator


class SummaryAgent:
    def __init__(self, ai_orchestrator: Optional[AIOrchestrator] = None):
        self.ai_orchestrator = ai_orchestrator
    
    
    def generate_trip_summary(
        self,
        trip_data: Dict[str, Any],
        incidents: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Generate comprehensive post-trip safety summary.
        """
        start_time = datetime.fromisoformat(trip_data.get("start_time", datetime.utcnow().isoformat()))
        end_time = datetime.fromisoformat(trip_data.get("end_time", datetime.utcnow().isoformat()))
        duration_minutes = int((end_time - start_time).total_seconds() / 60)
        
        deterministic_summary = self._generate_deterministic_summary(
            trip_data, incidents, duration_minutes
        )
        
        ai_summary = None
        if self.ai_orchestrator:
            try:
                ai_summary = self.ai_orchestrator.generate_trip_summary(
                    trip_data=trip_data,
                    incidents=incidents
                )
            except Exception as e:
                print(f"AI summary generation failed: {e}")
        
        final_summary = ai_summary if ai_summary else deterministic_summary
        
        return {
            **final_summary,
            "trip_stats": {
                "duration_minutes": duration_minutes,
                "distance_km": trip_data.get("distance_km", 0),
                "incidents_encountered": len(incidents),
                "reroutes_taken": trip_data.get("reroute_count", 0)
            },
            "generated_at": datetime.utcnow().isoformat(),
            "ai_generated": ai_summary is not None
        }
    
    
    def generate_area_insights(
        self,
        area: Dict[str, float],
        reports: List[Dict[str, Any]],
        time_range_hours: int = 24
    ) -> Dict[str, Any]:
        """
        Generate safety insights for a specific area.
        """
        recent_reports = [
            r for r in reports
            if self._is_within_hours(r.get("timestamp"), time_range_hours)
        ]
        
        category_breakdown = {}
        severity_sum = 0
        
        for report in recent_reports:
            category = report.get("category", "other")
            category_breakdown[category] = category_breakdown.get(category, 0) + 1
            severity_sum += report.get("severity", 1)
        
        avg_severity = severity_sum / len(recent_reports) if recent_reports else 0
        
        older_reports_count = len(reports) - len(recent_reports)
        if older_reports_count > 0:
            trend = "worsening" if len(recent_reports) > older_reports_count else "improving"
        else:
            trend = "stable"
        
        peak_hours = self._calculate_peak_risk_hours(recent_reports)
        safest_hours = self._calculate_safest_hours(peak_hours)
        
        ai_recommendations = [
            "Avoid this area during peak risk hours" if peak_hours else "Area shows moderate activity",
            "Consider alternative routes during night hours" if any(h >= 20 or h < 6 for h in peak_hours) else "Day travel appears safer",
            "Stay in well-lit, populated areas" if avg_severity > 3 else "Exercise normal caution"
        ]
        
        return {
            "area_summary": f"{len(recent_reports)} incidents reported in the last {time_range_hours} hours",
            "total_reports": len(recent_reports),
            "trend": trend,
            "peak_risk_hours": peak_hours,
            "safest_hours": safest_hours,
            "category_breakdown": category_breakdown,
            "avg_severity": round(avg_severity, 2),
            "ai_recommendations": ai_recommendations,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    
    def _generate_deterministic_summary(
        self,
        trip_data: Dict[str, Any],
        incidents: List[Dict[str, Any]],
        duration: int
    ) -> Dict[str, Any]:
        """Generate summary without AI"""
        critical_incidents = [i for i in incidents if i.get("severity", 1) >= 4]
        
        if not incidents:
            rating = "safe"
            summary = f"Trip completed safely in {duration} minutes with no incidents reported."
        elif critical_incidents:
            rating = "unsafe"
            summary = f"Trip completed with {len(critical_incidents)} critical safety concerns encountered."
        elif len(incidents) > 5:
            rating = "some_concerns"
            summary = f"Trip completed with {len(incidents)} minor safety reports along the route."
        else:
            rating = "mostly_safe"
            summary = f"Trip completed with minimal safety concerns ({len(incidents)} reports)."
        
        return {
            "overall_safety_rating": rating,
            "summary": summary,
            "safety_highlights": [] if incidents else ["No safety incidents reported"],
            "areas_of_concern": [f"{i.get('category', 'incident')} at segment {i.get('segment', 'unknown')}" for i in critical_incidents],
            "suggestions_for_next_time": self._generate_suggestions(incidents),
            "commendations": "Great job staying safe!" if not critical_incidents else "Stay vigilant on future trips."
        }
    
    
    def _generate_suggestions(self, incidents: List[Dict[str, Any]]) -> List[str]:
        """Generate safety suggestions based on incidents"""
        suggestions = []
        
        categories = [i.get("category") for i in incidents]
        
        if "poor_lighting" in categories:
            suggestions.append("Consider traveling during daylight hours when possible")
        
        if "harassment" in categories or "suspicious_activity" in categories:
            suggestions.append("Share your live location with trusted contacts during travel")
        
        if "isolated_area" in categories:
            suggestions.append("Choose routes through populated, well-lit areas")
        
        if len(incidents) > 3:
            suggestions.append("Consider using alternative routes for this destination")
        
        return suggestions or ["Continue following safe travel practices"]
    
    
    def _is_within_hours(self, timestamp_str: Optional[str], hours: int) -> bool:
        """Check if timestamp is within last N hours"""
        if not timestamp_str:
            return False
        try:
            timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
            age = (datetime.utcnow() - timestamp).total_seconds() / 3600
            return age <= hours
        except:
            return False
    
    
    def _calculate_peak_risk_hours(self, reports: List[Dict[str, Any]]) -> List[int]:
        """Identify hours with most incidents"""
        hour_counts = {}
        
        for report in reports:
            timestamp_str = report.get("timestamp")
            if timestamp_str:
                try:
                    timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                    hour = timestamp.hour
                    hour_counts[hour] = hour_counts.get(hour, 0) + 1
                except:
                    continue
        
        if not hour_counts:
            return []
        
        avg_count = sum(hour_counts.values()) / len(hour_counts)
        peak_hours = [hour for hour, count in hour_counts.items() if count > avg_count]
        
        return sorted(peak_hours)
    
    
    def _calculate_safest_hours(self, peak_hours: List[int]) -> List[int]:
        """Identify safest hours (inverse of peak)"""
        all_hours = set(range(24))
        peak_set = set(peak_hours)
        safest = list(all_hours - peak_set)
        
        daytime_safe = [h for h in safest if 6 <= h <= 18]
        
        return sorted(daytime_safe) if daytime_safe else sorted(safest)[:6]