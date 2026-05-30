"""
api/views/__init__.py
Re-exports semua views sehingga api/urls.py bisa tetap pakai `from . import views`.
"""
from api.views.auth import (
    health_check,
    register_user,
    login_user,
    logout_user,
    get_current_user,
    supabase_webhook,
)
from api.views.profile import (
    get_profile,
    update_profile,
)
from api.views.food import (
    list_food_records,
    create_food_record,
    get_food_record,
    delete_food_record,
)
from api.views.dashboard import (
    dashboard_summary,
)
from api.views.konsultasi import (
    create_konsultasi,
    list_konsultasi,
    update_konsultasi,
    delete_konsultasi,
    list_chat,
    send_chat,
    delete_chat,
)
from api.views.coachbot import (
    coachbot_chat,
)

__all__ = [
    'health_check',
    'register_user', 'login_user', 'logout_user', 'get_current_user', 'supabase_webhook',
    'get_profile', 'update_profile',
    'list_food_records', 'create_food_record', 'get_food_record', 'delete_food_record',
    'dashboard_summary',
    'create_konsultasi', 'list_konsultasi', 'update_konsultasi', 'delete_konsultasi',
    'list_chat', 'send_chat', 'delete_chat',
    'coachbot_chat',
]
