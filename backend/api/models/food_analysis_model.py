"""Data access layer for the 'food_analysis' table."""

from api.supabase_client import supabase


class FoodAnalysisModel:
    """Data access for the 'food_analysis' Supabase table."""

    TABLE = "food_analysis"

    @classmethod
    def find_by_user(cls, user_id, order: str = "tanggal.desc", extra_params: dict = None) -> list:
        """Find all food analysis records for a user, with optional filters."""
        params = {
            "id_user": f"eq.{user_id}",
            "order": order,
        }
        if extra_params:
            params.update(extra_params)
        return supabase.select(cls.TABLE, params)

    @classmethod
    def find_by_id_and_user(cls, record_id, user_id) -> dict | None:
        """Find a single record by id_analysis and id_user."""
        rows = supabase.select(
            cls.TABLE,
            {
                "id_analysis": f"eq.{record_id}",
                "id_user": f"eq.{user_id}",
            },
        )
        return rows[0] if rows else None

    @classmethod
    def create(cls, data: dict) -> dict:
        """Insert a new food analysis record."""
        return supabase.insert(cls.TABLE, data)

    @classmethod
    def delete(cls, record_id, user_id) -> bool:
        """Delete a food analysis record by id_analysis and id_user."""
        return supabase.delete(
            cls.TABLE,
            {
                "id_analysis": record_id,
                "id_user": user_id,
            },
        )
