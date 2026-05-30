"""
Coach chat controller: chat consultation (live chat between user & nutritionist).
Thin HTTP layer — delegates to CoachChatService.
"""

from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status

from api.services import CoachChatService


@api_view(["GET"])
@authentication_classes([])
@permission_classes([AllowAny])
def list_chat(request, consultation_id):
    """Get all chat messages for a consultation session."""
    try:
        rows = CoachChatService.list_chat(consultation_id)
        return Response(rows)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["POST"])
@authentication_classes([])
@permission_classes([AllowAny])
def send_chat(request, consultation_id):
    """Send a chat message. sender: 'user' or 'nutritionist'."""
    try:
        result = CoachChatService.send_chat(
            consultation_id,
            request.data.get("sender", "user"),
            request.data.get("message", ""),
        )
        return Response(result, status=status.HTTP_201_CREATED)
    except ValueError as e:
        error_msg = str(e)
        if "not found" in error_msg:
            return Response({"error": error_msg}, status=status.HTTP_404_NOT_FOUND)
        return Response({"error": error_msg}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["DELETE"])
@authentication_classes([])
@permission_classes([AllowAny])
def delete_chat(request, chat_id):
    """Delete a chat message."""
    try:
        CoachChatService.delete_chat(chat_id)
        return Response({"message": "Chat deleted successfully."})
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
