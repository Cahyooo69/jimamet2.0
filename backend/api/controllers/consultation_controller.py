"""
Consultation controller: consultation (referral) management.
Thin HTTP layer — delegates to ConsultationService.
"""

from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from api.services import ConsultationService


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_consultation(request):
    """User (CoachBot) creates a consultation request to nutritionist."""
    try:
        result = ConsultationService.create_consultation(
            request.user.id,
            request.data.get("coach_message", ""),
        )
        return Response(result, status=status.HTTP_201_CREATED)
    except ValueError as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["GET"])
@authentication_classes([])
@permission_classes([AllowAny])
def list_consultations(request):
    """Nutritionist views all incoming consultations."""
    try:
        result = ConsultationService.list_consultations()
        return Response(result)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["PATCH"])
@authentication_classes([])
@permission_classes([AllowAny])
def update_consultation(request, consultation_id):
    """Nutritionist updates consultation status & notes."""
    try:
        result = ConsultationService.update_consultation(
            consultation_id,
            request.data,
        )
        return Response(result)
    except ValueError as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["DELETE"])
@authentication_classes([])
@permission_classes([AllowAny])
def delete_consultation(request, consultation_id):
    """Nutritionist deletes a consultation session."""
    try:
        ConsultationService.delete_consultation(consultation_id)
        return Response({"message": "Consultation deleted successfully."})
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["GET"])
@authentication_classes([])
@permission_classes([AllowAny])
def get_patient_details(request, consultation_id):
    """Nutritionist gets patient profile and food history for a consultation."""
    try:
        result = ConsultationService.get_patient_details(consultation_id)
        return Response(result)
    except ValueError as e:
        return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
