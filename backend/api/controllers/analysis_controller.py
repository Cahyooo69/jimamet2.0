"""
Analysis controller: food records CRUD + dashboard summary.
Thin HTTP layer — delegates to AnalysisService.
"""

from datetime import date

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from api.services import AnalysisService


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def list_food_records(request):
    """List all food consumption records for the current user."""
    try:
        date_from = request.query_params.get("date_from")
        date_to = request.query_params.get("date_to")
        rows = AnalysisService.list_food_records(
            request.user.id,
            date_from,
            date_to,
        )
        return Response(rows)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_food_record(request):
    """Create a new food consumption record."""
    try:
        result = AnalysisService.create_food_record(
            request.user.id,
            request.data,
        )
        return Response(result, status=status.HTTP_201_CREATED)
    except ValueError as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_food_record(request, record_id):
    """Get a single food record."""
    try:
        result = AnalysisService.get_food_record(request.user.id, record_id)
        return Response(result)
    except ValueError as e:
        return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def delete_food_record(request, record_id):
    """Delete a food record."""
    try:
        AnalysisService.delete_food_record(request.user.id, record_id)
        return Response({"message": "Record deleted."}, status=status.HTTP_204_NO_CONTENT)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def dashboard_summary(request):
    """Get daily nutrition summary for dashboard."""
    try:
        target_date = request.query_params.get("date", date.today().isoformat())
        result = AnalysisService.get_dashboard_summary(
            request.user.id,
            target_date,
        )
        return Response(result)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
