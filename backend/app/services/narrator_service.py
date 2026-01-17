"""
app/services/narrator_service.py
Narration service for Safety Route backend.
Converts safety data into clear, user-friendly messages.
"""

from typing import Optional, Dict, Any


def narrate_route_safety(
    risk_score: int,
    risk_level: str,
    context: Optional[Dict[str, Any]] = None
) -> str:
    try:
        context = context or {}
        time_of_day = context.get("time_of_day", "")
        area_name = context.get("area_name", "")
        
        risk_level_normalized = str(risk_level).strip().lower() if risk_level else "unknown"
        
        if risk_level_normalized in ["low", "safe", "green"]:
            base_msg = "This route looks safe"
            if time_of_day:
                base_msg += f" for {time_of_day} travel"
            if area_name:
                base_msg += f" through {area_name}"
            base_msg += ". Well-lit streets and good foot traffic expected."
            return base_msg
        
        elif risk_level_normalized in ["medium", "moderate", "yellow", "caution"]:
            base_msg = "This route has moderate activity"
            if area_name:
                base_msg += f" in {area_name}"
            base_msg += ". Stay aware of your surroundings. Consider sharing your trip with someone."
            return base_msg
        
        elif risk_level_normalized in ["high", "danger", "red", "unsafe"]:
            base_msg = "This route passes through areas with higher risk"
            if time_of_day:
                base_msg += f" during {time_of_day}"
            base_msg += ". We recommend an alternative route. If you must proceed, stay alert and keep emergency contacts ready."
            return base_msg
        
        else:
            return f"Route assessed with safety score {risk_score}. Please review the details carefully before proceeding."
    
    except Exception:
        return "Route safety information is available. Please review before proceeding."


def narrate_alert(
    alert_type: str,
    location_label: Optional[str] = None
) -> str:
    try:
        alert_type_normalized = str(alert_type).strip().lower() if alert_type else "general"
        location_part = f" near {location_label}" if location_label else ""
        
        alert_messages = {
            "unsafe_zone": f"You're approaching an area with increased risk{location_part}. Consider taking an alternate path.",
            "unsafe": f"You're approaching an area with increased risk{location_part}. Consider taking an alternate path.",
            "crowd": f"High crowd density detected{location_part}. Stay cautious and keep your belongings secure.",
            "crowded": f"High crowd density detected{location_part}. Stay cautious and keep your belongings secure.",
            "low_light": f"Limited street lighting ahead{location_part}. Stay on main roads if possible.",
            "dark": f"Limited street lighting ahead{location_part}. Stay on main roads if possible.",
            "crime_hotspot": f"This area has recent safety reports{location_part}. We suggest rerouting for your safety.",
            "crime": f"This area has recent safety reports{location_part}. We suggest rerouting for your safety.",
            "emergency": "Emergency services have been notified. Help is on the way. Stay calm and find a safe, visible location.",
            "sos": "SOS alert sent to your emergency contacts. They've been notified of your location. Stay where you are if safe.",
            "sos_activated": "SOS alert sent to your emergency contacts. They've been notified of your location. Stay where you are if safe.",
            "reroute": f"A safer route is available{location_part}. Would you like to switch?",
            "traffic": f"Heavy traffic detected{location_part}. Consider an alternate route.",
            "weather": f"Weather conditions may affect safety{location_part}. Please take precautions.",
        }
        
        message = alert_messages.get(alert_type_normalized)
        
        if message:
            return message
        else:
            return f"Safety alert{location_part}. Please stay cautious and aware of your surroundings."
    
    except Exception:
        return "Safety alert received. Please stay cautious and aware of your surroundings."