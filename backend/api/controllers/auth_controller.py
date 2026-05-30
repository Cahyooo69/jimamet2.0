"""
Auth controller: register, login, logout, me, webhook.
Thin HTTP layer — delegates to AuthService.
"""

from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from api.services import AuthService


@api_view(["GET"])
@permission_classes([AllowAny])
def health_check(request):
    """Health check endpoint."""
    return Response(
        {
            "status": "ok",
            "service": "Jimamet Medical Nutrition API",
            "version": "2.0.0",
        }
    )


@api_view(["POST"])
@permission_classes([AllowAny])
def register_user(request):
    """Register user baru — semua data disimpan ke Supabase."""
    try:
        extra_data = {
            "age": request.data.get("age") or None,
            "weight": request.data.get("weight") or None,
            "height": request.data.get("height") or None,
            "activity_level": request.data.get("activity_level", "moderate"),
        }
        result = AuthService.register(
            username=request.data.get("username", ""),
            email=request.data.get("email", ""),
            password=request.data.get("password", ""),
            full_name=request.data.get("full_name", ""),
            extra_data=extra_data,
        )
        return Response(
            {
                "message": "Registrasi berhasil.",
                "token": result["token"],
                "user": {
                    "id": result["user_id"],
                    "username": result["username"],
                    "email": result["email"],
                    "full_name": result["full_name"],
                },
            },
            status=status.HTTP_201_CREATED,
        )
    except ValueError as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["POST"])
@permission_classes([AllowAny])
def login_user(request):
    """Login — validasi kredensial dari Supabase."""
    try:
        result = AuthService.login(
            username=request.data.get("username", ""),
            password=request.data.get("password", ""),
        )
        return Response(result)
    except ValueError as e:
        return Response({"error": str(e)}, status=status.HTTP_401_UNAUTHORIZED)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout_user(request):
    """Logout — hapus token dari Supabase."""
    AuthService.logout(request.user)
    return Response({"message": "Logout berhasil."})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_current_user(request):
    """Get info user yang sedang login."""
    result = AuthService.get_current_user(request.user)
    return Response(result)


@api_view(["POST"])
@permission_classes([AllowAny])
def supabase_webhook(request):
    """Webhook dari Supabase — dipanggil otomatis saat user dihapus."""
    try:
        webhook_secret = getattr(settings, "SUPABASE_WEBHOOK_SECRET", "")
        incoming_secret = request.headers.get("x-webhook-secret", "")
        result = AuthService.handle_webhook(
            request.data,
            webhook_secret,
            incoming_secret,
        )
        return Response(result)
    except PermissionError:
        return Response({"error": "Unauthorized."}, status=status.HTTP_401_UNAUTHORIZED)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
