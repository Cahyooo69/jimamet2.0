"""Data access layer for the 'chat_konsultasi' table."""

from api.supabase_client import supabase


class ChatKonsultasiModel:
    """Data access for the 'chat_konsultasi' Supabase table."""

    TABLE = "chat_konsultasi"

    @classmethod
    def find_by_konsultasi(cls, konsultasi_id, order: str = "tanggal.asc") -> list:
        """Find all chat messages for a konsultasi session."""
        return supabase.select(
            cls.TABLE,
            {
                "id_konsultasi": f"eq.{konsultasi_id}",
                "order": order,
            },
        )

    @classmethod
    def create(cls, data: dict) -> dict:
        """Insert a new chat message."""
        return supabase.insert(cls.TABLE, data)

    @classmethod
    def delete(cls, chat_id) -> bool:
        """Delete a chat message by id_chat."""
        return supabase.delete(cls.TABLE, {"id_chat": chat_id})
