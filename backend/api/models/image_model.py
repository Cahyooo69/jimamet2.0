"""Data access layer for the 'images' table."""

from api.supabase_client import supabase


class ImageModel:
    """Data access for the 'images' Supabase table."""

    TABLE = "images"

    @classmethod
    def find_by_user(cls, user_id) -> list:
        """Find all images for a user."""
        return supabase.select(cls.TABLE, {"user_id": f"eq.{user_id}"})

    @classmethod
    def find_by_id(cls, image_id) -> dict | None:
        """Find an image by id."""
        rows = supabase.select(cls.TABLE, {"id": f"eq.{image_id}"})
        return rows[0] if rows else None

    @classmethod
    def create(cls, data: dict) -> dict:
        """Insert a new image record."""
        return supabase.insert(cls.TABLE, data)

    @classmethod
    def delete(cls, image_id) -> bool:
        """Delete an image record by id."""
        return supabase.delete(cls.TABLE, {"id": image_id})
