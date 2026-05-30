"""
Profile controller: get and update user profile.
Thin HTTP layer — delegates to ProfileService.
"""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from api.services import ProfileService


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_profile(request):
    """Get the current user's profile from Supabase."""
    try:
        result = ProfileService.get_profile(request.user)
        return Response(result)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["PUT", "PATCH"])
@permission_classes([IsAuthenticated])
def update_profile(request):
    """Update the current user's profile in Supabase."""
    try:
        result = ProfileService.update_profile(request.user, request.data)
        return Response(result)
    except ValueError as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
