"""
Notification controller: konsultasi (referral) management.
Thin HTTP layer — delegates to NotificationService.
"""

from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from api.services import NotificationService


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_konsultasi(request):
    """User (CoachBot) membuat permintaan konsultasi ke ahli gizi."""
    try:
        result = NotificationService.create_konsultasi(
            request.user.id,
            request.data.get("pesan_coachbot", ""),
        )
        return Response(result, status=status.HTTP_201_CREATED)
    except ValueError as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["GET"])
@authentication_classes([])
@permission_classes([AllowAny])
def list_konsultasi(request):
    """Ahli gizi melihat semua daftar konsultasi yang masuk."""
    try:
        result = NotificationService.list_konsultasi()
        return Response(result)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["PATCH"])
@authentication_classes([])
@permission_classes([AllowAny])
def update_konsultasi(request, konsultasi_id):
    """Ahli gizi mengupdate status & catatan konsultasi."""
    try:
        result = NotificationService.update_konsultasi(
            konsultasi_id,
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
def delete_konsultasi(request, konsultasi_id):
    """Ahli gizi menghapus sesi konsultasi."""
    try:
        NotificationService.delete_konsultasi(konsultasi_id)
        return Response({"message": "Konsultasi deleted successfully."})
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
