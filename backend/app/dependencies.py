"""Reusable FastAPI dependencies shared by route modules."""
from app.database import get_db

__all__ = ["get_db"]
