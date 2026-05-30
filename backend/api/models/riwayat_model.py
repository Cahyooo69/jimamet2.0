"""Data access layer for the 'history' (riwayat) table."""

from api.supabase_client import supabase


class RiwayatModel:
    """Data access for the 'history' Supabase table."""

    TABLE = "history"

    @classmethod
    def find_by_user(cls, user_id) -> list:
        """Find all history records for a user."""
        return supabase.select(cls.TABLE, {"id_user": f"eq.{user_id}"})

    @classmethod
    def find_by_user_and_date(cls, user_id, date_str: str) -> dict | None:
        """Find a history record for a user on a specific date."""
        rows = supabase.select(
            cls.TABLE,
            {
                "id_user": f"eq.{user_id}",
                "tanggal": f"eq.{date_str}",
            },
        )
        return rows[0] if rows else None

    @classmethod
    def create(cls, data: dict) -> dict:
        """Insert a new history record."""
        return supabase.insert(cls.TABLE, data)

    @classmethod
    def update(cls, history_id, data: dict) -> dict:
        """Update a history record by id_history."""
        return supabase.update(cls.TABLE, {"id_history": history_id}, data)

    @classmethod
    def delete(cls, history_id) -> bool:
        """Delete a history record by id_history."""
        return supabase.delete(cls.TABLE, {"id_history": history_id})
