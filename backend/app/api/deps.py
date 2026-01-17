"""
app/api/deps.py
Shared FastAPI dependency functions for Safety Route backend.
"""

import uuid
from datetime import datetime
from typing import Optional


def get_request_id() -> str:
    return str(uuid.uuid4())


def get_current_timestamp() -> str:
    return datetime.utcnow().isoformat() + "Z"


def get_db():
    from app.core.database import get_db as _get_db
    return _get_db()


def get_user_id(user_id: Optional[str] = None) -> str:
    if user_id:
        return user_id
    return f"user_{uuid.uuid4().hex[:8]}"