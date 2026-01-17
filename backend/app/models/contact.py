from pydantic import BaseModel, Field
from typing import Optional


class EmergencyContact(BaseModel):
    contact_id: str
    name: str = Field(..., min_length=1)
    phone_number: str = Field(..., pattern=r'^\+?[1-9]\d{1,14}$')
    relation: Optional[str] = None
    priority: int = Field(default=1, ge=1, le=10)
    is_active: bool = True