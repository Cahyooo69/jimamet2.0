"""Data access layer for the 'coach_messages' table."""

from api.supabase_client import supabase


class CoachMessageModel:
    """Data access for the 'coach_messages' Supabase table."""

    TABLE = "coach_messages"

    @classmethod
    def find_by_session(cls, session_id, order: str = "sent_at.asc") -> list:
        """Find all chat messages for a coach session."""
        return supabase.select(
            cls.TABLE,
            {
                "session_id": f"eq.{session_id}",
                "order": order,
            },
        )

    @classmethod
    def create(cls, data: dict) -> dict:
        """Insert a new chat message."""
        return supabase.insert(cls.TABLE, data)

    @classmethod
    def delete(cls, message_id) -> bool:
        """Delete a chat message by id."""
        return supabase.delete(cls.TABLE, {"id": message_id})
