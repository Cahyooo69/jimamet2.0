"""
Business logic for user profile management.
Profile data is cached for 5 minutes per user.
"""

import logging
from api.models import UserModel
from api import cache as app_cache

logger = logging.getLogger(__name__)


class ProfileService:
    """User profile business logic with caching."""

    @classmethod
    def get_profile(cls, user) -> dict:
        """Fetch the user's profile from cache or Supabase."""
        cache_key = app_cache.key_profile(user.id)
        cached = app_cache.get(cache_key)
        if cached is not None:
            return cached

        row = UserModel.find_by_id(user.id)
        if row:
            result = {
                "user_id": user.id,
                "full_name": row.get("full_name"),
                "email": row.get("email"),
                "username": user.username,
                "age": row.get("age"),
                "weight": row.get("weight"),
                "height": row.get("height"),
                "gender": row.get("gender"),
                "activity_level": row.get("activity_level", "moderate"),
                "goal": row.get("goal"),
            }
        else:
            result = {
                "user_id": user.id,
                "full_name": user.get_full_name(),
                "email": user.email,
                "username": user.username,
                "age": None,
                "weight": None,
                "height": None,
                "gender": None,
                "activity_level": "moderate",
                "goal": None,
            }

        app_cache.set(cache_key, result, app_cache.TTL_PROFILE)
        return result

    @classmethod
    def update_profile(cls, user, data: dict) -> dict:
        """
        Update the user's profile. Invalidates cache on success.
        Raises ValueError if no valid fields provided.
        """
        allowed_fields = [
            "full_name", "age", "weight", "height",
            "gender", "activity_level", "goal",
        ]

        normalized = {}
        for k, v in data.items():
            if k in allowed_fields and v is not None:
                normalized[k] = v

        if not normalized:
            raise ValueError("No valid fields to update.")

        logger.info("update_profile: user_id=%s, fields=%s", user.id, list(normalized.keys()))

        existing = UserModel.find_by_id(user.id)
        if existing:
            result = UserModel.update(user.id, normalized)
        else:
            normalized["email"] = user.email
            normalized["id"] = user.id
            if "full_name" not in normalized:
                normalized["full_name"] = user.get_full_name()
            result = UserModel.create(normalized)

        # Invalidate caches that depend on profile data
        app_cache.delete(app_cache.key_profile(user.id))
        app_cache.delete(app_cache.key_auth_token(""))  # Can't target exact token, but TTL handles it

        return {"message": "Profil berhasil diperbarui.", "data": result}
