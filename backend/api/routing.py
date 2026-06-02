"""
WebSocket URL routing for Django Channels.
"""

from django.urls import re_path
from api.consumers import ConsultationChatConsumer

websocket_urlpatterns = [
    re_path(r"ws/consultation/(?P<consultation_id>[^/]+)/$", ConsultationChatConsumer.as_asgi()),
]
