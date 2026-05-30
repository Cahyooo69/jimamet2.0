"""
Lightweight cache utility for Jimamet.
Wraps Django's cache framework with typed helpers and TTL constants.
"""

import hashlib
from django.core.cache import cache

# TTL Constants (seconds)

TTL_AUTH_TOKEN = 300  # 5 min — token → user lookup
TTL_PROFILE = 300  # 5 min — user profile data
TTL_DASHBOARD = 60  # 1 min — dashboard summary
TTL_FOOD_RECORDS = 60  # 1 min — food record listing
TTL_COACH_SESSIONS = 30  # 30s  — coach session listing
TTL_COACH_MESSAGES = 30  # 30s  — messages within a session


# Key Builders
def _key(prefix: str, *parts) -> str:
    """Build a cache key from prefix and parts."""
    return f"jm:{prefix}:{':'.join(str(p) for p in parts)}"


def key_auth_token(token: str) -> str:
    """Cache key for token auth — hashed for safety."""
    h = hashlib.sha256(token.encode()).hexdigest()[:16]
    return _key("auth", h)


def key_profile(user_id) -> str:
    return _key("profile", user_id)


def key_dashboard(user_id, date_str: str) -> str:
    return _key("dash", user_id, date_str)


def key_food_records(user_id) -> str:
    return _key("food", user_id)


def key_coach_sessions(user_id) -> str:
    return _key("csess", user_id)


def key_coach_session_detail(session_id) -> str:
    return _key("csdet", session_id)


# Cache Operations
def get(key: str):
    """Get a value from cache. Returns None on miss."""
    return cache.get(key)


def set(key: str, value, ttl: int):
    """Set a value in cache with TTL in seconds."""
    cache.set(key, value, ttl)


def delete(key: str):
    """Delete a single cache key."""
    cache.delete(key)


def invalidate_user(user_id):
    """Invalidate all cached data for a user (profile, dashboard, food, sessions)."""
    cache.delete(key_profile(user_id))
    cache.delete(key_food_records(user_id))
    cache.delete(key_coach_sessions(user_id))
    # Dashboard keys include date, so we can't easily clear all of them.
    # But TTL is only 60s, so they expire quickly.
