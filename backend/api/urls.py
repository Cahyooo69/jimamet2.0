"""
Jimamet API URL Configuration.
"""

from django.urls import path
from . import views

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

    # Konsultasi (CoachBot → Ahli Gizi)
    path('konsultasi/', views.list_konsultasi, name='list_konsultasi'),
    path('konsultasi/create/', views.create_konsultasi, name='create_konsultasi'),
    path('konsultasi/<str:konsultasi_id>/update/', views.update_konsultasi, name='update_konsultasi'),
    path('konsultasi/<str:konsultasi_id>/delete/', views.delete_konsultasi, name='delete_konsultasi'),

    # Chat Konsultasi (User ↔ Ahli Gizi)
    path('konsultasi/<str:konsultasi_id>/chat/', views.list_chat, name='list_chat'),
    path('konsultasi/<str:konsultasi_id>/chat/send/', views.send_chat, name='send_chat'),
    path('chat/<str:chat_id>/delete/', views.delete_chat, name='delete_chat'),

    # NutriCoach AI Chat
    path('coachbot/chat/', views.coachbot_chat, name='coachbot_chat'),
]
