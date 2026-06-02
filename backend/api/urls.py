"""
Jimamet API URL Configuration.
"""

from django.urls import path
from api import controllers as views

urlpatterns = [
    # Health
    path('health/', views.health_check, name='health_check'),

    # Auth
    path('auth/register/', views.register_user, name='register'),
    path('auth/login/', views.login_user, name='login'),
    path('auth/logout/', views.logout_user, name='logout'),
    path('auth/me/', views.get_current_user, name='current_user'),
    path('auth/webhook/supabase/', views.supabase_webhook, name='supabase_webhook'),

    # User Profile
    path('profile/', views.get_profile, name='get_profile'),
    path('profile/update/', views.update_profile, name='update_profile'),

    # Food Records
    path('food/', views.list_food_records, name='list_food_records'),
    path('food/create/', views.create_food_record, name='create_food_record'),
    path('food/<str:record_id>/', views.get_food_record, name='get_food_record'),
    path('food/<str:record_id>/delete/', views.delete_food_record, name='delete_food_record'),

    # Dashboard
    path('dashboard/summary/', views.dashboard_summary, name='dashboard_summary'),

    # Consultations (CoachBot → Nutritionist referral)
    path('consultations/', views.list_consultations, name='list_consultations'),
    path('consultations/create/', views.create_consultation, name='create_consultation'),
    path('consultations/<str:consultation_id>/update/', views.update_consultation, name='update_consultation'),
    path('consultations/<str:consultation_id>/delete/', views.delete_consultation, name='delete_consultation'),
    path('consultations/<str:consultation_id>/patient/', views.get_patient_details, name='get_patient_details'),

    # Consultation Chat (User ↔ Nutritionist)
    path('consultations/<str:consultation_id>/chat/', views.list_chat, name='list_chat'),
    path('consultations/<str:consultation_id>/chat/send/', views.send_chat, name='send_chat'),
    path('chat/<str:chat_id>/delete/', views.delete_chat, name='delete_chat'),

    # NutriCoach AI Chat (Session-based)
    path('coach/sessions/', views.list_sessions, name='list_sessions'),
    path('coach/sessions/create/', views.create_session, name='create_session'),
    path('coach/sessions/<str:session_id>/', views.get_session, name='get_session'),
    path('coach/sessions/<str:session_id>/delete/', views.delete_session, name='delete_session'),
    path('coach/sessions/<str:session_id>/chat/', views.coachbot_chat, name='coachbot_chat'),

    # ML YOLO Detection
    path('detect-food/', views.detect_food_api, name='detect_food_api'),
]
