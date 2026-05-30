"""Data access layer for the 'daily_summary' table."""

from api.supabase_client import supabase


class DailySummaryModel:
    """Data access for the 'daily_summary' Supabase table."""

    TABLE = "daily_summary"

    @classmethod
    def find_by_user(cls, user_id) -> list:
        """Find all summary records for a user."""
        return supabase.select(cls.TABLE, {"user_id": f"eq.{user_id}"})

    @classmethod
    def find_by_user_and_date(cls, user_id, date_str: str) -> dict | None:
        """Find a summary record for a user on a specific date."""
        rows = supabase.select(
            cls.TABLE,
            {
                "user_id": f"eq.{user_id}",
                "date": f"eq.{date_str}",
            },
        )
        return rows[0] if rows else None

    @classmethod
    def create(cls, data: dict) -> dict:
        """Insert a new daily summary record."""
        return supabase.insert(cls.TABLE, data)

    @classmethod
    def update(cls, summary_id, data: dict) -> dict:
        """Update a daily summary record by id."""
        return supabase.update(cls.TABLE, {"id": summary_id}, data)

    @classmethod
    def delete(cls, summary_id) -> bool:
        """Delete a daily summary record by id."""
        return supabase.delete(cls.TABLE, {"id": summary_id})
