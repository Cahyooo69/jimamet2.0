"""Data access layer for the 'consultations' table."""

from api.supabase_client import supabase


class ConsultationModel:
    """Data access for the 'consultations' Supabase table."""

    TABLE = "consultations"

    @classmethod
    def find_all(cls, order: str = "created_at.desc") -> list:
        """Find all consultations records."""
        return supabase.select(cls.TABLE, {"order": order})

    @classmethod
    def find_by_id(cls, consultation_id) -> dict | None:
        """Find a consultation by id."""
        rows = supabase.select(cls.TABLE, {"id": f"eq.{consultation_id}"})
        return rows[0] if rows else None

    @classmethod
    def find_by_user(cls, user_id) -> list:
        """Find all consultation records for a user."""
        return supabase.select(cls.TABLE, {"user_id": f"eq.{user_id}"})

    @classmethod
    def create(cls, data: dict) -> dict:
        """Insert a new consultation record."""
        return supabase.insert(cls.TABLE, data)

    @classmethod
    def update(cls, consultation_id, data: dict) -> dict:
        """Update a consultation record by id."""
        return supabase.update(cls.TABLE, {"id": consultation_id}, data)

    @classmethod
    def delete(cls, consultation_id) -> bool:
        """Delete a consultation record by id."""
        return supabase.delete(cls.TABLE, {"id": consultation_id})
