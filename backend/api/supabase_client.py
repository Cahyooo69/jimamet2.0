import logging
import requests
from django.conf import settings

logger = logging.getLogger(__name__)


class SupabaseClient:
    """REST client for Supabase with connection pooling."""

    def __init__(self):
        self.rest_url = settings.SUPABASE_REST_URL.rstrip("/")
        self.api_key = settings.SUPABASE_KEY

        # Persistent session — reuses TCP/TLS connections across requests
        self._session = requests.Session()
        self._session.headers.update(
            {
                "apikey": self.api_key,
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "Prefer": "return=representation",
            }
        )

    def _url(self, table: str) -> str:
        return f"{self.rest_url}/{table}"

    def _handle_response(self, resp, operation: str, table: str):
        """Handle Supabase response, raising descriptive errors."""
        if not resp.ok:
            try:
                body = resp.json()
                msg = body.get("message", body.get("error", resp.text))
            except Exception:
                msg = resp.text
            logger.error(
                "Supabase %s on '%s' failed (%d): %s",
                operation,
                table,
                resp.status_code,
                msg,
            )
            raise RuntimeError(f"Supabase {operation} on '{table}' failed ({resp.status_code}): {msg}")
        return resp

    def select(self, table: str, params: dict = None) -> list:
        """SELECT rows from a table."""
        resp = self._session.get(
            self._url(table),
            params=params or {},
            timeout=10,
        )
        self._handle_response(resp, "SELECT", table)
        return resp.json()

    def insert(self, table: str, data: dict) -> dict:
        """INSERT a single row."""
        resp = self._session.post(
            self._url(table),
            json=data,
            timeout=10,
        )
        self._handle_response(resp, "INSERT", table)
        result = resp.json()
        return result[0] if isinstance(result, list) and result else result

    def update(self, table: str, match: dict, data: dict) -> dict:
        """UPDATE rows matching filters."""
        params = {k: f"eq.{v}" for k, v in match.items()}
        resp = self._session.patch(
            self._url(table),
            params=params,
            json=data,
            timeout=10,
        )
        self._handle_response(resp, "UPDATE", table)
        result = resp.json()
        if isinstance(result, list):
            if not result:
                logger.warning(
                    "Supabase UPDATE on '%s' matched 0 rows (match=%s)",
                    table,
                    match,
                )
                return {}
            return result[0]
        return result

    def delete(self, table: str, match: dict) -> bool:
        """DELETE rows matching filters."""
        params = {k: f"eq.{v}" for k, v in match.items()}
        resp = self._session.delete(
            self._url(table),
            params=params,
            timeout=10,
        )
        self._handle_response(resp, "DELETE", table)
        return True


# Singleton instance
supabase = SupabaseClient()
