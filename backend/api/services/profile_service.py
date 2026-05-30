"""
Business logic for user profile management.
"""

from api.models import UserModel


class ProfileService:
    """User profile business logic."""

    @classmethod
    def get_profile(cls, user) -> dict:
        """Fetch the user's profile from Supabase."""
        row = UserModel.find_by_id(user.id)
        if row:
            return {
                "user_id": user.id,
                "full_name": row.get("nama"),
                "email": row.get("email"),
                "username": user.username,
                "age": row.get("umur"),
                "weight": row.get("berat_badan"),
                "height": row.get("tinggi_badan"),
                "gender": row.get("jenis_kelamin"),
                "activity_level": row.get("aktivitas_harian", "moderate"),
                "goal": row.get("goal"),
            }
        else:
            return {
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

    @classmethod
    def update_profile(cls, user, data: dict) -> dict:
        """
        Update the user's profile.

        Raises ValueError if no valid fields provided.
        """
        allowed_fields = [
            "full_name",
            "age",
            "weight",
            "height",
            "gender",
            "activity_level",
            "goal",
        ]
        update_data = {k: v for k, v in data.items() if k in allowed_fields}

        if not update_data:
            raise ValueError("No valid fields to update.")

        # Map API field names to database column names
        field_map = {
            "full_name": "nama",
            "age": "umur",
            "weight": "berat_badan",
            "height": "tinggi_badan",
            "activity_level": "aktivitas_harian",
        }
        mapped_data = {}
        for api_key, value in update_data.items():
            db_key = field_map.get(api_key, api_key)
            mapped_data[db_key] = value

        existing = UserModel.find_by_id(user.id)
        if existing:
            result = UserModel.update(user.id, mapped_data)
        else:
            mapped_data["email"] = user.email
            mapped_data["id_user"] = user.id
            if "nama" not in mapped_data:
                mapped_data["nama"] = user.get_full_name()
            result = UserModel.create(mapped_data)

        return {"message": "Profil berhasil diperbarui.", "data": result}
