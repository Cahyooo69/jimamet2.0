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
        from datetime import timedelta
        d = date.fromisoformat(today)
        seven_days_ago = (d - timedelta(days=6)).isoformat()

        # Ambil detail makanan 7 hari terakhir dari food_analysis
        food_rows = supabase.select('food_analysis', {
            'id_user': f'eq.{user_id}',
            'tanggal': f'gte.{seven_days_ago}T00:00:00',
        })

        # Helper untuk konversi UTC string ke format tanggal lokal (YYYY-MM-DD)
        def get_local_date_str(iso_str):
            if not iso_str: return ''
            # Simple timezone adjustment (User is in +07:00)
            try:
                from datetime import datetime, timedelta
                # Hapus Z atau offset
                clean_str = iso_str.split('+')[0].replace('Z', '')
                dt = datetime.fromisoformat(clean_str)
                # Tambah 7 jam untuk WIB timezone
                dt_local = dt + timedelta(hours=7)
                return dt_local.strftime('%Y-%m-%d')
            except:
                return iso_str[:10]

        # Pisahkan makanan hari ini
        today_rows = [r for r in food_rows if get_local_date_str(r.get('tanggal', '')) == today]

        # Kalkulasi rekap harian untuk bar chart
        weekly_cals = { (d - timedelta(days=i)).isoformat(): 0 for i in range(7) }
        for r in food_rows:
            date_str = get_local_date_str(r.get('tanggal', ''))
            if date_str in weekly_cals:
                weekly_cals[date_str] += float(r.get('kalori') or 0)
        
        weekly_data = []
        for i in range(6, -1, -1):
            dt = (d - timedelta(days=i)).isoformat()
            weekly_data.append({
                'date': dt,
                'calories': weekly_cals[dt]
            })

        # Kalkulasi langsung dari food_analysis untuk hari ini
        total_cal = sum(float(r.get('kalori', 0) or 0) for r in today_rows)
        total_protein = sum(float(r.get('protein', 0) or 0) for r in today_rows)
        total_fat = sum(float(r.get('lemak', 0) or 0) for r in today_rows)
        total_carbs = sum(float(r.get('karbohidrat', 0) or 0) for r in today_rows)

        return Response({
            'date': today,
            'total_meals': len(today_rows),
            'total_calories': total_cal,
            'total_protein': total_protein,
            'total_carbs': total_carbs,
            'total_fat': total_fat,
            'total_fiber': 0,
            'meals': today_rows,
            'weekly_data': weekly_data,
        })
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
