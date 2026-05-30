"""Data access layer for the 'konsultasi' (notification) table."""

from api.supabase_client import supabase


class NotificationModel:
    """Data access for the 'konsultasi' Supabase table."""

    TABLE = "konsultasi"

    @classmethod
    def find_all(cls, order: str = "tanggal.desc") -> list:
        """Find all konsultasi records."""
        return supabase.select(cls.TABLE, {"order": order})

    @classmethod
    def find_by_id(cls, konsultasi_id) -> dict | None:
        """Find a konsultasi by id_konsultasi."""
        rows = supabase.select(cls.TABLE, {"id_konsultasi": f"eq.{konsultasi_id}"})
        return rows[0] if rows else None

    @classmethod
    def find_by_user(cls, user_id) -> list:
        """Find all konsultasi records for a user."""
        return supabase.select(cls.TABLE, {"id_user": f"eq.{user_id}"})

    @classmethod
    def create(cls, data: dict) -> dict:
        """Insert a new konsultasi record."""
        return supabase.insert(cls.TABLE, data)

    @classmethod
    def update(cls, konsultasi_id, data: dict) -> dict:
        """Update a konsultasi record by id_konsultasi."""
        return supabase.update(cls.TABLE, {"id_konsultasi": konsultasi_id}, data)

    @classmethod
    def delete(cls, konsultasi_id) -> bool:
        """Delete a konsultasi record by id_konsultasi."""
        return supabase.delete(cls.TABLE, {"id_konsultasi": konsultasi_id})
