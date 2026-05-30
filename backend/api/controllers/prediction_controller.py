"""
Prediction controller: NutriCoach AI chat.
Thin HTTP layer — delegates to PredictionService.
"""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from api.services import PredictionService


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def coachbot_chat(request):
    """
    Endpoint untuk ngobrol dengan NutriCoach AI (Gemini).
    Menerima text dari user, merespons sebagai ahli gizi pintar.
    """
    try:
        result = PredictionService.chat(
            request.user.id,
            request.data.get("message", ""),
        )
        return Response(result)
    except ValueError as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except RuntimeError as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
