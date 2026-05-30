"""Data access layer for the 'consultation_messages' table."""

from api.supabase_client import supabase


class ConsultationMessageModel:
    """Data access for the 'consultation_messages' Supabase table."""

    TABLE = "consultation_messages"

    @classmethod
    def find_by_consultation(cls, consultation_id, order: str = "sent_at.asc") -> list:
        """Find all chat messages for a consultation session."""
        return supabase.select(
            cls.TABLE,
            {
                "consultation_id": f"eq.{consultation_id}",
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
