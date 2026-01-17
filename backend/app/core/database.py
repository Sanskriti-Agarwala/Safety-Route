"""
app/core/database.py
Lightweight database abstraction for Safety Route backend.
Provides in-memory storage for hackathon MVP.
"""

import threading
from typing import Any, Dict, Optional

# Global in-memory storage
_storage: Dict[str, Dict[str, Any]] = {}
_lock = threading.Lock()
_connected = False


def connect() -> None:
    """Initialize database connection (in-memory for MVP)."""
    global _connected
    with _lock:
        if not _connected:
            _storage.clear()
            _storage.update({
                "users": {},
                "trips": {},
                "reports": {},
                "emergencies": {},
                "contacts": {}
            })
            _connected = True
            print("[DATABASE] Connected to in-memory storage")


def disconnect() -> None:
    """Close database connection and clear storage."""
    global _connected
    with _lock:
        if _connected:
            _storage.clear()
            _connected = False
            print("[DATABASE] Disconnected and cleared storage")


def get_db() -> Dict[str, Dict[str, Any]]:
    """
    Get reference to in-memory database.
    Returns dictionary with table-like collections.
    """
    if not _connected:
        connect()
    return _storage


def is_connected() -> bool:
    """Check if database is connected."""
    return _connected


def reset_storage() -> None:
    """Reset all collections to empty state (useful for testing)."""
    with _lock:
        for collection in _storage.values():
            collection.clear()
        print("[DATABASE] Storage reset")