"""
Supabase client utility for Jimamet.
Handles direct REST API calls to Supabase for app data storage.
"""

import requests
from django.conf import settings


class SupabaseClient:
    """Simple REST client for Supabase."""

    def __init__(self):
        self.rest_url = settings.SUPABASE_REST_URL.rstrip("/")
        self.api_key = settings.SUPABASE_KEY
        self.headers = {
            "apikey": self.api_key,
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Prefer": "return=representation",
        }

    def _url(self, table: str) -> str:
        return f"{self.rest_url}/{table}"

    # ── SELECT ──
    def select(self, table: str, params: dict = None) -> list:
        """SELECT rows from a table. params are query parameters (e.g. filters)."""
        resp = requests.get(
            self._url(table),
            headers=self.headers,
            params=params or {},
            timeout=10,
        )
        resp.raise_for_status()
        return resp.json()

    # ── INSERT ──
    def insert(self, table: str, data: dict) -> dict:
        """INSERT a single row."""
        resp = requests.post(
            self._url(table),
            headers=self.headers,
            json=data,
            timeout=10,
        )
        resp.raise_for_status()
        result = resp.json()
        return result[0] if isinstance(result, list) and result else result

    # ── UPDATE ──
    def update(self, table: str, match: dict, data: dict) -> dict:
        """UPDATE rows matching filters. match is {column: value}."""
        params = {f"{k}": f"eq.{v}" for k, v in match.items()}
        resp = requests.patch(
            self._url(table),
            headers=self.headers,
            params=params,
            json=data,
            timeout=10,
        )
        resp.raise_for_status()
        result = resp.json()
        return result[0] if isinstance(result, list) and result else result

    # ── DELETE ──
    def delete(self, table: str, match: dict) -> bool:
        """DELETE rows matching filters."""
        params = {f"{k}": f"eq.{v}" for k, v in match.items()}
        resp = requests.delete(
            self._url(table),
            headers=self.headers,
            params=params,
            timeout=10,
        )
        resp.raise_for_status()
        return True


# Singleton instance
supabase = SupabaseClient()
