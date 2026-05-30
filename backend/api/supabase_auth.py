"""
supabase_auth.py — Custom DRF authentication backend menggunakan Supabase.
Menggantikan Django User model + rest_framework.authtoken sepenuhnya.
Token lookups are cached in-memory for performance.
"""

import secrets

from django.contrib.auth.hashers import make_password, check_password as _check_password
from django.contrib.auth.models import AnonymousUser
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

from api.supabase_client import supabase
from api import cache as app_cache

# ── Password Utilities ──────────────────────────────────────────────────────


def hash_password(raw_password: str) -> str:
    """Hash password menggunakan Django PBKDF2 hasher (aman)."""
    return make_password(raw_password)


def verify_password(raw_password: str, hashed: str) -> bool:
    """Verifikasi password plain text terhadap hash-nya."""
    return _check_password(raw_password, hashed)


def generate_token() -> str:
    """Generate token sesi acak yang aman secara kriptografis."""
    return secrets.token_hex(20)


# ── User Objects ─────────────────────────────────────────────────────────────


class SupabaseUser(AnonymousUser):
    """
    Custom user model representing a normal user authenticated via Supabase token.
    Uses English naming matching schema v2.
    """
    is_active = True
    is_authenticated = True
    role = "user"

    def __init__(self, user_data: dict):
        self.id = user_data.get("id")
        self.username = user_data.get("username")
        self.email = user_data.get("email")
        self.full_name = user_data.get("full_name", "")
        self.raw_data = user_data

    @property
    def is_anonymous(self):
        return False

    def __str__(self):
        return self.username or self.email or str(self.id)

    def get_full_name(self):
        return self.full_name


class AhliGiziUser(AnonymousUser):
    """
    Custom user model representing a Nutritionist (Ahli Gizi).
    """
    is_active = True
    is_authenticated = True
    role = "nutritionist"

    def __init__(self, user_data: dict):
        self.id = user_data.get("id")
        self.username = user_data.get("username")
        self.email = user_data.get("email")
        self.full_name = user_data.get("full_name", "")
        self.specialization = user_data.get("specialization", "")
        self.raw_data = user_data

    @property
    def is_anonymous(self):
        return False

    def __str__(self):
        return f"Nutritionist: {self.username}"

    def get_full_name(self):
        return self.full_name


# ── DRF Authentication Class ─────────────────────────────────────────────────


class SupabaseTokenAuthentication(BaseAuthentication):
    """
    DRF authentication backend yang memvalidasi token langsung ke Supabase.
    Token lookups are cached for 5 minutes to avoid hitting Supabase on every request.

    Header yang diharapkan:
        Authorization: Token <token>
    """

    def authenticate(self, request):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Token "):
            return None

        token = auth_header[6:].strip()
        if not token:
            return None

        # Ahli gizi token: format 'ahligizi_<uuid>'
        if token.startswith("ahligizi_"):
            return self._authenticate_ahli_gizi(token)

        # User biasa: cek di tabel users (with cache)
        return self._authenticate_user(token)

    def _authenticate_user(self, token: str):
        cache_key = app_cache.key_auth_token(token)

        # Check cache first
        cached = app_cache.get(cache_key)
        if cached is not None:
            return (SupabaseUser(cached), token)

        try:
            rows = supabase.select("users", {"token": f"eq.{token}"})
            if not rows:
                raise AuthenticationFailed("Token tidak valid atau sudah kedaluwarsa.")

            user_data = rows[0]
            # Cache the user data
            app_cache.set(cache_key, user_data, app_cache.TTL_AUTH_TOKEN)

            return (SupabaseUser(user_data), token)
        except AuthenticationFailed:
            raise
        except Exception:
            raise AuthenticationFailed("Gagal memverifikasi token.")

    def _authenticate_ahli_gizi(self, token: str):
        cache_key = app_cache.key_auth_token(token)

        cached = app_cache.get(cache_key)
        if cached is not None:
            return (AhliGiziUser(cached), token)

        try:
            ahli_id = token.replace("ahligizi_", "")
            rows = supabase.select("nutritionists", {"id": f"eq.{ahli_id}"})
            if not rows:
                raise AuthenticationFailed("Token ahli gizi tidak valid.")

            user_data = rows[0]
            app_cache.set(cache_key, user_data, app_cache.TTL_AUTH_TOKEN)

            return (AhliGiziUser(user_data), token)
        except AuthenticationFailed:
            raise
        except Exception:
            raise AuthenticationFailed("Gagal memverifikasi token ahli gizi.")

    def authenticate_header(self, request):
        return "Token"
