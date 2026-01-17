"""
app/services/sos_service.py
Emergency SOS service for Safety Route backend.
Handles emergency trigger logic and notification preparation.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any


def trigger_sos(
    user_id: str,
    latitude: float,
    longitude: float,
    timestamp: Optional[str] = None,
    trusted_contacts: Optional[List[str]] = None
) -> Dict[str, Any]:
    try:
        if timestamp is None:
            timestamp = datetime.utcnow().isoformat() + "Z"
        
        if trusted_contacts is None or len(trusted_contacts) == 0:
            trusted_contacts = [
                "emergency_contact_1@example.com",
                "emergency_contact_2@example.com"
            ]
        
        notified_contacts = []
        for contact in trusted_contacts:
            _simulate_notification(
                contact=contact,
                user_id=user_id,
                latitude=latitude,
                longitude=longitude,
                timestamp=timestamp
            )
            notified_contacts.append(contact)
        
        response = {
            "status": "sent",
            "user_id": user_id,
            "location": {
                "latitude": latitude,
                "longitude": longitude
            },
            "notified_contacts": notified_contacts,
            "timestamp": timestamp
        }
        
        print(f"[SOS] Emergency alert triggered for user {user_id} at ({latitude}, {longitude})")
        print(f"[SOS] Notified {len(notified_contacts)} contacts: {', '.join(notified_contacts)}")
        
        return response
    
    except Exception as e:
        print(f"[SOS ERROR] Failed to trigger SOS: {str(e)}")
        return {
            "status": "failed",
            "user_id": user_id,
            "location": {
                "latitude": latitude,
                "longitude": longitude
            },
            "notified_contacts": [],
            "timestamp": timestamp or datetime.utcnow().isoformat() + "Z",
            "error": str(e)
        }


def _simulate_notification(
    contact: str,
    user_id: str,
    latitude: float,
    longitude: float,
    timestamp: str
) -> None:
    message = f"""
    [EMERGENCY ALERT]
    User: {user_id}
    Time: {timestamp}
    Location: {latitude}, {longitude}
    Map Link: https://maps.google.com/?q={latitude},{longitude}
    
    This is an automated emergency notification from Safety Route.
    """
    
    print(f"[SOS NOTIFICATION] Sending to {contact}:")
    print(message.strip())