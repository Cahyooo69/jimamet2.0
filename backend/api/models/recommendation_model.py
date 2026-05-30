"""Data access layer for the 'recommendations' table."""

from api.supabase_client import supabase


class RecommendationModel:
    """Data access for the 'recommendations' Supabase table."""

    TABLE = "recommendations"

    @classmethod
    def find_by_user(cls, user_id) -> list:
        """Find all recommendations for a user."""
        return supabase.select(cls.TABLE, {"user_id": f"eq.{user_id}"})

    @classmethod
    def create(cls, data: dict) -> dict:
        """Insert a new recommendation record."""
        return supabase.insert(cls.TABLE, data)

    @classmethod
    def delete(cls, recommendation_id) -> bool:
        """Delete a recommendation record by id."""
        return supabase.delete(cls.TABLE, {"id": recommendation_id})
