"""
supabase_auth.py — Custom DRF authentication backend menggunakan Supabase.
Menggantikan Django User model + rest_framework.authtoken sepenuhnya.
"""

import secrets

from django.contrib.auth.hashers import make_password, check_password as _check_password
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

from api.supabase_client import supabase

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


class SupabaseUser:
    """
    Object user ringan yang dibackup oleh baris tabel 'users' di Supabase.
    id_user = BIGSERIAL (integer auto-increment)
    username = kolom terpisah (TEXT UNIQUE)
    """

    is_authenticated = True
    is_superuser = False
    is_staff = False
    role = "user"

    def __init__(self, row: dict):
        self.id = row.get("id_user")  # integer (BIGSERIAL)
        self.username = row.get("username", "")
        self.email = row.get("email", "")
        self._nama = row.get("nama", "")

    def get_full_name(self) -> str:
        return self._nama

    def __str__(self):
        return self.username


class AhliGiziUser:
    """Object user untuk ahli gizi, dibackup oleh tabel 'ahli_gizi' di Supabase."""

    is_authenticated = True
    is_superuser = False
    is_staff = False
    role = "ahli_gizi"

    def __init__(self, row: dict):
        self.id = str(row.get("id_ahli_gizi", ""))
        self.username = row.get("username", "")
        self.email = row.get("email", "")
        self._nama = row.get("nama", "")

    def get_full_name(self) -> str:
        return self._nama

    def __str__(self):
        return self.username


# ── DRF Authentication Class ─────────────────────────────────────────────────


class SupabaseTokenAuthentication(BaseAuthentication):
    """
    DRF authentication backend yang memvalidasi token langsung ke Supabase.
    Mendukung user biasa (tabel users) dan ahli gizi (tabel ahli_gizi).

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

        # User biasa: cek di tabel users
        return self._authenticate_user(token)

    def _authenticate_user(self, token: str):
        try:
            rows = supabase.select("users", {"token": f"eq.{token}"})
            if not rows:
                raise AuthenticationFailed("Token tidak valid atau sudah kedaluwarsa.")
            return (SupabaseUser(rows[0]), token)
        except AuthenticationFailed:
            raise
        except Exception:
            raise AuthenticationFailed("Gagal memverifikasi token.")

    def _authenticate_ahli_gizi(self, token: str):
        try:
            ahli_id = token.replace("ahligizi_", "")
            rows = supabase.select("ahli_gizi", {"id_ahli_gizi": f"eq.{ahli_id}"})
            if not rows:
                raise AuthenticationFailed("Token ahli gizi tidak valid.")
            return (AhliGiziUser(rows[0]), token)
        except AuthenticationFailed:
            raise
        except Exception:
            raise AuthenticationFailed("Gagal memverifikasi token ahli gizi.")

    def authenticate_header(self, request):
        return "Token"
