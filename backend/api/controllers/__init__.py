"""
api/controllers/__init__.py
Re-exports semua controller views sehingga api/urls.py bisa pakai `from api import controllers`.
"""
from api.controllers.auth_controller import (
    health_check,
    register_user,
    login_user,
    logout_user,
    get_current_user,
    supabase_webhook,
)
from api.controllers.profile_controller import (
    get_profile,
    update_profile,
)
from api.controllers.analysis_controller import (
    list_food_records,
    create_food_record,
    get_food_record,
    delete_food_record,
    dashboard_summary,
)
from api.controllers.notification_controller import (
    create_konsultasi,
    list_konsultasi,
    update_konsultasi,
    delete_konsultasi,
)
from api.controllers.coachbot_controller import (
    list_chat,
    send_chat,
    delete_chat,
)
from api.controllers.prediction_controller import (
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
