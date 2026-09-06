"""Database connectivity helpers for supported SQL backends."""

from app.database.connection import DatabaseConnection, DatabaseError

__all__ = ["DatabaseConnection", "DatabaseError"]
