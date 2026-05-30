"""Data access layer for the 'food_records' table."""

from api.supabase_client import supabase


class FoodRecordModel:
    """Data access for the 'food_records' Supabase table."""

    TABLE = "food_records"

    @classmethod
    def find_by_user(cls, user_id, order: str = "recorded_at.desc", extra_params: dict = None) -> list:
        """Find all food analysis records for a user, with optional filters."""
        params = {
            "user_id": f"eq.{user_id}",
            "order": order,
        }
        if extra_params:
            params.update(extra_params)
        return supabase.select(cls.TABLE, params)

    @classmethod
    def find_by_id_and_user(cls, record_id, user_id) -> dict | None:
        """Find a single record by id and user_id."""
        rows = supabase.select(
            cls.TABLE,
            {
                "id": f"eq.{record_id}",
                "user_id": f"eq.{user_id}",
            },
        )
        return rows[0] if rows else None

    @classmethod
    def create(cls, data: dict) -> dict:
        """Insert a new food analysis record."""
        return supabase.insert(cls.TABLE, data)

    @classmethod
    def delete(cls, record_id, user_id) -> bool:
        """Delete a food analysis record by id and user_id."""
        return supabase.delete(
            cls.TABLE,
            {
                "id": record_id,
                "user_id": user_id,
            },
        )
