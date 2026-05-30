"""Data access layer for the 'users' table."""

from api.supabase_client import supabase


class UserModel:
    """Data access for the 'users' Supabase table."""

    TABLE = "users"

    @classmethod
    def find_by_id(cls, user_id) -> dict | None:
        """Find a user by id (BIGSERIAL)."""
        rows = supabase.select(cls.TABLE, {"id": f"eq.{user_id}"})
        return rows[0] if rows else None

    @classmethod
    def find_by_username(cls, username: str) -> dict | None:
        """Find a user by username."""
        rows = supabase.select(cls.TABLE, {"username": f"eq.{username}"})
        return rows[0] if rows else None

    @classmethod
    def find_by_email(cls, email: str) -> dict | None:
        """Find a user by email."""
        rows = supabase.select(cls.TABLE, {"email": f"eq.{email}"})
        return rows[0] if rows else None

    @classmethod
    def find_by_token(cls, token: str) -> dict | None:
        """Find a user by session token."""
        rows = supabase.select(cls.TABLE, {"token": f"eq.{token}"})
        return rows[0] if rows else None

    @classmethod
    def create(cls, data: dict) -> dict:
        """Insert a new user row."""
        return supabase.insert(cls.TABLE, data)

    @classmethod
    def update(cls, user_id, data: dict) -> dict:
        """Update a user row by id."""
        return supabase.update(cls.TABLE, {"id": user_id}, data)

    @classmethod
    def delete(cls, user_id) -> bool:
        """Delete a user row by id."""
        return supabase.delete(cls.TABLE, {"id": user_id})
