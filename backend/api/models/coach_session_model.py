"""Data access layer for the 'coach_sessions' table."""

from api.supabase_client import supabase


class CoachSessionModel:
    """Data access for the 'coach_sessions' Supabase table."""

    TABLE = "coach_sessions"

    @classmethod
    def find_by_user(cls, user_id) -> list:
        """Find all coach sessions for a user, ordered by updated_at descending."""
        return supabase.select(
            cls.TABLE,
            {
                "user_id": f"eq.{user_id}",
                "order": "updated_at.desc",
            },
        )

    @classmethod
    def find_by_id(cls, session_id) -> dict | None:
        """Find a coach session by id."""
        rows = supabase.select(cls.TABLE, {"id": f"eq.{session_id}"})
        return rows[0] if rows else None

    @classmethod
    def find_by_id_and_user(cls, session_id, user_id) -> dict | None:
        """Find a coach session by id and user_id."""
        rows = supabase.select(
            cls.TABLE,
            {
                "id": f"eq.{session_id}",
                "user_id": f"eq.{user_id}",
            },
        )
        return rows[0] if rows else None

    @classmethod
    def create(cls, data: dict) -> dict:
        """Insert a new coach session."""
        return supabase.insert(cls.TABLE, data)

    @classmethod
    def update(cls, session_id, data: dict) -> dict:
        """Update a coach session by id."""
        return supabase.update(cls.TABLE, {"id": session_id}, data)

    @classmethod
    def delete(cls, session_id) -> bool:
        """Delete a coach session by id."""
        return supabase.delete(cls.TABLE, {"id": session_id})
