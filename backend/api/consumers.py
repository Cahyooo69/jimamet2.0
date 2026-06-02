"""
WebSocket consumer for real-time consultation chat.
Uses Django Channels with in-memory channel layer.
"""

import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer

logger = logging.getLogger(__name__)


class ConsultationChatConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for consultation chat rooms.
    URL: ws://localhost:8000/ws/consultation/<consultation_id>/
    
    Messages sent/received format:
    {
        "type": "chat_message",
        "message": "...",
        "sender": "user" | "nutritionist",
        "sent_at": "ISO timestamp"
    }
    """

    async def connect(self):
        self.consultation_id = self.scope["url_route"]["kwargs"]["consultation_id"]
        self.room_group_name = f"consultation_{self.consultation_id}"

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name,
        )
        await self.accept()
        logger.info("WebSocket connected: %s", self.room_group_name)

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name,
        )
        logger.info("WebSocket disconnected: %s", self.room_group_name)

    async def receive(self, text_data):
        """Receive message from WebSocket client and broadcast to room."""
        data = json.loads(text_data)

        # Broadcast to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "message": data.get("message", ""),
                "sender": data.get("sender", "user"),
                "sent_at": data.get("sent_at", ""),
                "id": data.get("id", ""),
            },
        )

    async def chat_message(self, event):
        """Receive message from room group and send to WebSocket client."""
        await self.send(text_data=json.dumps({
            "type": "chat_message",
            "id": event.get("id", ""),
            "message": event["message"],
            "sender": event["sender"],
            "sent_at": event["sent_at"],
        }))
