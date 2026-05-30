"""
Coachbot controller: chat konsultasi (live chat between user & ahli gizi).
Thin HTTP layer — delegates to CoachbotService.
"""

from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status

from api.services import CoachbotService


@api_view(["GET"])
@authentication_classes([])
@permission_classes([AllowAny])
def list_chat(request, konsultasi_id):
    """Ambil semua pesan chat untuk satu sesi konsultasi."""
    try:
        rows = CoachbotService.list_chat(konsultasi_id)
        return Response(rows)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["POST"])
@authentication_classes([])
@permission_classes([AllowAny])
def send_chat(request, konsultasi_id):
    """Kirim pesan chat. pengirim: 'user' atau 'ahli_gizi'."""
    try:
        result = CoachbotService.send_chat(
            konsultasi_id,
            request.data.get("pengirim", "user"),
            request.data.get("pesan", ""),
        )
        return Response(result, status=status.HTTP_201_CREATED)
    except ValueError as e:
        error_msg = str(e)
        if "tidak ditemukan" in error_msg:
            return Response({"error": error_msg}, status=status.HTTP_404_NOT_FOUND)
        return Response({"error": error_msg}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["DELETE"])
@authentication_classes([])
@permission_classes([AllowAny])
def delete_chat(request, chat_id):
    """Hapus pesan chat."""
    try:
        CoachbotService.delete_chat(chat_id)
        return Response({"message": "Chat deleted successfully."})
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
