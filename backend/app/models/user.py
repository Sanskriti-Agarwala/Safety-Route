from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional
from .contact import EmergencyContact


class User(BaseModel):
    user_id: str
    name: str = Field(..., min_length=1)
    email: Optional[EmailStr] = None
    phone_number: str = Field(..., pattern=r'^\+?[1-9]\d{1,14}$')
    emergency_contacts: list[EmergencyContact] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = True
    last_known_latitude: Optional[float] = Field(default=None, ge=-90, le=90)
    last_known_longitude: Optional[float] = Field(default=None, ge=-180, le=180)
    last_location_update: Optional[datetime] = None