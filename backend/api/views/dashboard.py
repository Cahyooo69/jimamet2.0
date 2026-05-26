"""
Dashboard views: daily nutrition summary.
"""
from datetime import date

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from api.supabase_client import supabase


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_summary(request):
    """Get daily nutrition summary for dashboard."""
    today = request.query_params.get('date', date.today().isoformat())
    user_id = str(request.user.id)

    try:
        # Ambil dari tabel history (rekap harian)
        history_rows = supabase.select('history', {
            'id_user': f'eq.{user_id}',
            'tanggal': f'eq.{today}',
        })

        # Ambil detail makanan hari ini dari food_analysis
        food_rows = supabase.select('food_analysis', {
            'id_user': f'eq.{user_id}',
            'tanggal': f'gte.{today}T00:00:00',
        })

        if history_rows:
            h = history_rows[0]
            total_cal = float(h.get('total_kalori', 0) or 0)
            total_protein = float(h.get('total_protein', 0) or 0)
            total_fat = float(h.get('total_lemak', 0) or 0)
            total_carbs = float(h.get('total_karbohidrat', 0) or 0)
        else:
            # Kalkulasi langsung dari food_analysis jika history belum ada
            total_cal = sum(float(r.get('kalori', 0) or 0) for r in food_rows)
            total_protein = sum(float(r.get('protein', 0) or 0) for r in food_rows)
            total_fat = sum(float(r.get('lemak', 0) or 0) for r in food_rows)
            total_carbs = sum(float(r.get('karbohidrat', 0) or 0) for r in food_rows)

        return Response({
            'date': today,
            'total_meals': len(food_rows),
            'total_calories': total_cal,
            'total_protein': total_protein,
            'total_carbs': total_carbs,
            'total_fat': total_fat,
            'total_fiber': 0,
            'meals': food_rows,
        })
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
