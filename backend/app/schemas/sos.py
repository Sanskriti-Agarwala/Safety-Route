from pydantic import BaseModel, Field
from typing import Optional, List


class SOSRequest(BaseModel):
    latitude: float = Field(..., ge=-90, le=90, description="Current latitude")
    longitude: float = Field(..., ge=-180, le=180, description="Current longitude")
    emergency_contacts: Optional[List[str]] = Field(None, description="List of emergency contact emails or phone numbers")
    message: Optional[str] = Field(None, max_length=500, description="Optional emergency message")
    user_id: Optional[str] = Field(None, description="User identifier")


class SOSResponse(BaseModel):
    success: bool
    message: str
    sos_id: str
    timestamp: str
    contacts_notified: str
    location_shared: str