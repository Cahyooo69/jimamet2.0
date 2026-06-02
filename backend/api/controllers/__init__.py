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
from api.controllers.consultation_controller import (
    create_consultation,
    list_consultations,
    update_consultation,
    delete_consultation,
    get_patient_details,
)
from api.controllers.coach_chat_controller import (
    list_chat,
    send_chat,
    delete_chat,
)
from api.controllers.prediction_controller import (
    coachbot_chat,
    list_sessions,
    create_session,
    get_session,
    delete_session,
)
from api.controllers.detection_controller import (
    detect_food_api,
)

__all__ = [
    'health_check',
    'register_user', 'login_user', 'logout_user', 'get_current_user', 'supabase_webhook',
    'get_profile', 'update_profile',
    'list_food_records', 'create_food_record', 'get_food_record', 'delete_food_record',
    'dashboard_summary',
    'create_consultation', 'list_consultations', 'update_consultation', 'delete_consultation', 'get_patient_details',
    'list_chat', 'send_chat', 'delete_chat',
    'coachbot_chat', 'list_sessions', 'create_session', 'get_session', 'delete_session',
    'detect_food_api',
]
