"""
Business logic for authentication: register, login, logout, webhook.
"""

import hmac

from api.models import UserModel
from api.supabase_client import supabase
from api.supabase_auth import hash_password, verify_password, generate_token


class AuthService:
    """Authentication business logic."""

    @classmethod
    def register(cls, username: str, email: str, password: str, full_name: str = "", extra_data: dict = None) -> dict:
        """
        Register a new user.

        Returns dict with keys: token, user_id, username, email, full_name.
        Raises ValueError on validation failure.
        """
        username = username.strip()
        email = email.strip()

        if not username or not email or not password:
            raise ValueError("Username, email, dan password wajib diisi.")

        # Check duplicates
        if UserModel.find_by_username(username):
            raise ValueError("Username sudah digunakan.")

        if UserModel.find_by_email(email):
            raise ValueError("Email sudah terdaftar.")

        # Hash password & generate session token
        password_hash = hash_password(password)
        token = generate_token()

        user_data = {
            "username": username,
            "full_name": full_name,
            "email": email,
            "password": password_hash,
            "token": token,
        }

        # Merge optional extra data
        if extra_data:
            field_map = {
                "age": "age",
                "weight": "weight",
                "height": "height",
                "activity_level": "activity_level",
            }
            for api_key, db_key in field_map.items():
                val = extra_data.get(api_key)
                if val is not None:
                    user_data[db_key] = val

        result = UserModel.create(user_data)
        user_id = result.get("id") if isinstance(result, dict) else None

        return {
            "token": token,
            "user_id": user_id,
            "username": username,
            "email": email,
            "full_name": full_name,
        }

    @classmethod
    def login(cls, username: str, password: str) -> dict:
        """
        Authenticate a user (nutritionist or regular user).

        Returns dict with keys: message, token, role (optional), user.
        Raises ValueError on failure.
        """
        username = username.strip()

        if not username or not password:
            raise ValueError("Username dan password wajib diisi.")

        # 1. Check nutritionists table first
        try:
            ahli_rows = supabase.select("nutritionists", {"username": f"eq.{username}"})
            if ahli_rows:
                ag = ahli_rows[0]
                if ag.get("password") == password:
                    return {
                        "message": "Login berhasil.",
                        "token": f'ahligizi_{ag["id"]}',
                        "role": "ahli_gizi",
                        "user": {
                            "id": ag["id"],
                            "username": ag["username"],
                            "email": ag.get("email", ""),
                            "full_name": ag.get("full_name", ""),
                            "specialization": ag.get("specialization", ""),
                            "license_number": ag.get("license_number", ""),
                        },
                    }
        except Exception:
            pass

        # 2. Check regular users table
        user_row = UserModel.find_by_username(username)
        if not user_row:
            raise ValueError("Username atau password salah.")

        if not verify_password(password, user_row.get("password", "")):
            raise ValueError("Username atau password salah.")

        # Rotate token on each login
        new_token = generate_token()
        UserModel.update(user_row["id"], {"token": new_token})

        return {
            "message": "Login berhasil.",
            "token": new_token,
            "user": {
                "id": user_row.get("id"),
                "username": user_row.get("username"),
                "email": user_row.get("email", ""),
                "full_name": user_row.get("full_name", ""),
            },
        }

    @classmethod
    def logout(cls, user) -> None:
        """Clear user session token. No-op for nutritionist."""
        if getattr(user, "role", "") == "nutritionist":
            return
        try:
            UserModel.update(user.id, {"token": None})
        except Exception:
            pass

    @classmethod
    def get_current_user(cls, user) -> dict:
        """Return current user info."""
        return {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "full_name": user.get_full_name(),
        }

    @classmethod
    def handle_webhook(cls, payload: dict, webhook_secret: str = "", incoming_secret: str = "") -> dict:
        """
        Process Supabase webhook events.

        Raises PermissionError if secret mismatch.
        """
        if webhook_secret:
            if not hmac.compare_digest(incoming_secret, webhook_secret):
                raise PermissionError("Unauthorized.")

        if payload.get("type") == "DELETE" and payload.get("table") == "users":
            id_user = payload.get("old_record", {}).get("id")
            return {"message": f"User {id_user} telah dihapus dari Supabase."}

        return {"message": "Event diabaikan."}
