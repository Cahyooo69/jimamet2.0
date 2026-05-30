"""
Prediction controller: NutriCoach AI chat.
Thin HTTP layer — delegates to PredictionService.
"""

import logging

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from api.services import PredictionService

logger = logging.getLogger(__name__)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def list_sessions(request):
    """List all AI chat sessions for current user."""
    try:
        result = PredictionService.list_sessions(request.user.id)
        return Response(result)
    except Exception as e:
        logger.exception("list_sessions error")
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_session(request):
    """Create a new AI chat session."""
    try:
        title = request.data.get("title", "New Consultation")
        logger.info("create_session: user_id=%s, title=%s", request.user.id, title)
        result = PredictionService.create_session(request.user.id, title)
        return Response(result, status=status.HTTP_201_CREATED)
    except Exception as e:
        logger.exception("create_session error")
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_session(request, session_id):
    """Get session details and all its messages."""
    try:
        result = PredictionService.get_session(request.user.id, session_id)
        return Response(result)
    except ValueError as e:
        return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.exception("get_session error")
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def delete_session(request, session_id):
    """Delete an AI chat session."""
    try:
        PredictionService.delete_session(request.user.id, session_id)
        return Response({"message": "Session deleted."})
    except ValueError as e:
        return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.exception("delete_session error")
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def coachbot_chat(request, session_id):
    """
    Endpoint untuk ngobrol dengan NutriCoach AI (Gemini).
    Menerima text dari user, merespons sebagai ahli gizi pintar.
    """
    try:
        result = PredictionService.chat(
            request.user.id,
            session_id,
            request.data.get("message", ""),
        )
        return Response(result)
    except ValueError as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except RuntimeError as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except Exception as e:
        logger.exception("coachbot_chat error")
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
