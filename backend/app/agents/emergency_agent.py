from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid

from app.ai.orchestrator import AIOrchestrator


class EmergencyAgent:
    def __init__(self, ai_orchestrator: Optional[AIOrchestrator] = None):
        self.ai_orchestrator = ai_orchestrator
        self.sos_history = []
    
    
    def handle_sos(
        self,
        location: Dict[str, float],
        user_info: Optional[Dict[str, Any]] = None,
        emergency_contacts: Optional[List[str]] = None,
        context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Handle emergency SOS trigger with AI-generated message.
        """
        sos_id = str(uuid.uuid4())
        timestamp = datetime.utcnow()
        
        user_message = None
        if context:
            user_message = context
        elif user_info:
            user_message = f"Emergency assistance needed by {user_info.get('name', 'user')}"
        
        ai_message = None
        if self.ai_orchestrator:
            try:
                ai_message = self.ai_orchestrator.generate_sos_message(
                    location=location,
                    user_info=user_info,
                    context=user_message
                )
            except Exception as e:
                print(f"AI SOS message generation failed: {e}")
        
        final_message = ai_message or self._generate_fallback_message(location, user_info)
        
        sos_record = {
            "sos_id": sos_id,
            "timestamp": timestamp.isoformat(),
            "location": location,
            "message": final_message,
            "user_info": user_info,
            "emergency_contacts": emergency_contacts or [],
            "status": "sent",
            "ai_generated": ai_message is not None
        }
        
        self.sos_history.append(sos_record)
        
        notification_result = self._send_notifications(sos_record)
        
        return {
            "success": True,
            "sos_id": sos_id,
            "timestamp": timestamp.isoformat(),
            "message": final_message,
            "contacts_notified": len(emergency_contacts or []),
            "notification_status": notification_result,
            "location_shared": f"{location.get('latitude')}, {location.get('longitude')}"
        }
    
    
    def assess_emergency_severity(
        self,
        situation: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Assess the severity of an emergency situation.
        """
        severity_score = 50
        factors = []
        
        if situation.get("immediate_danger"):
            severity_score += 30
            factors.append("immediate_danger_reported")
        
        if situation.get("isolated_location"):
            severity_score += 20
            factors.append("isolated_location")
        
        if situation.get("night_time"):
            severity_score += 15
            factors.append("night_time")
        
        nearby_help = situation.get("nearby_safety_infrastructure", [])
        if not nearby_help:
            severity_score += 10
            factors.append("no_nearby_help")
        else:
            severity_score -= 10
            factors.append("safety_infrastructure_nearby")
        
        severity_score = max(0, min(100, severity_score))
        
        if severity_score >= 75:
            severity_level = "critical"
            recommended_action = "contact_emergency_services"
        elif severity_score >= 50:
            severity_level = "high"
            recommended_action = "alert_contacts_immediately"
        elif severity_score >= 30:
            severity_level = "medium"
            recommended_action = "notify_contacts"
        else:
            severity_level = "low"
            recommended_action = "monitor_situation"
        
        return {
            "severity_score": severity_score,
            "severity_level": severity_level,
            "contributing_factors": factors,
            "recommended_action": recommended_action,
            "requires_immediate_response": severity_score >= 75,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    
    def generate_safety_instructions(
        self,
        situation_type: str
    ) -> Dict[str, Any]:
        """
        Generate safety instructions for different emergency scenarios.
        """
        instructions = {
            "harassment": {
                "immediate_actions": [
                    "Move to a well-lit, populated area immediately",
                    "Call emergency services if feeling threatened",
                    "Don't engage with the person - keep moving"
                ],
                "contact_priority": "high",
                "call_emergency": True
            },
            "isolated_area": {
                "immediate_actions": [
                    "Share your live location with trusted contacts",
                    "Stay on the phone with someone you trust",
                    "Move toward main roads or populated areas"
                ],
                "contact_priority": "medium",
                "call_emergency": False
            },
            "accident": {
                "immediate_actions": [
                    "Call emergency services immediately",
                    "Move to safety if possible",
                    "Provide your exact location to responders"
                ],
                "contact_priority": "critical",
                "call_emergency": True
            },
            "suspicious_activity": {
                "immediate_actions": [
                    "Do not investigate - leave the area",
                    "Report to local authorities",
                    "Alert others in the area if safe to do so"
                ],
                "contact_priority": "medium",
                "call_emergency": False
            }
        }
        
        return instructions.get(situation_type, {
            "immediate_actions": [
                "Assess your safety",
                "Contact emergency services if needed",
                "Share your location with trusted contacts"
            ],
            "contact_priority": "medium",
            "call_emergency": False
        })
    
    
    def _generate_fallback_message(
        self,
        location: Dict[str, float],
        user_info: Optional[Dict[str, Any]]
    ) -> str:
        """Generate emergency message without AI"""
        lat = location.get("latitude", "unknown")
        lon = location.get("longitude", "unknown")
        
        name = user_info.get("name", "A user") if user_info else "A user"
        
        return (
            f"🚨 EMERGENCY ALERT 🚨\n\n"
            f"{name} has triggered an SOS alert and needs immediate assistance.\n\n"
            f"📍 Location: {lat}, {lon}\n"
            f"🕐 Time: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}\n\n"
            f"Please check on them immediately or contact emergency services."
        )
    
    
    def _send_notifications(self, sos_record: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate sending notifications to emergency contacts"""
        contacts = sos_record.get("emergency_contacts", [])
        
        return {
            "sms_sent": len(contacts),
            "email_sent": len(contacts),
            "push_notifications": len(contacts),
            "success": True,
            "simulated": True
        }