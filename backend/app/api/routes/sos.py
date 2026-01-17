from fastapi import APIRouter
from datetime import datetime
import uuid

from app.schemas.sos import SOSRequest, SOSResponse

router = APIRouter(prefix="/sos", tags=["emergency"])

sos_alerts_storage = []


@router.post("", response_model=SOSResponse)
async def trigger_sos(request: SOSRequest):
    sos_id = str(uuid.uuid4())
    timestamp = datetime.utcnow().isoformat()
    
    alert_data = {
        "sos_id": sos_id,
        "latitude": request.latitude,
        "longitude": request.longitude,
        "emergency_contacts": request.emergency_contacts,
        "message": request.message,
        "timestamp": timestamp,
        "status": "sent"
    }
    
    sos_alerts_storage.append(alert_data)
    
    simulated_contacts = ", ".join(request.emergency_contacts) if request.emergency_contacts else "default emergency services"
    
    return SOSResponse(
        success=True,
        message=f"SOS alert sent successfully to {len(request.emergency_contacts or [])} contact(s)",
        sos_id=sos_id,
        timestamp=timestamp,
        contacts_notified=simulated_contacts,
        location_shared=f"{request.latitude}, {request.longitude}"
    )


@router.get("/history")
async def get_sos_history():
    return {
        "total_alerts": len(sos_alerts_storage),
        "alerts": sos_alerts_storage
    }