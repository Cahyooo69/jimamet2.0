"""
Food analysis views: list, create, get, delete food records.
"""
from datetime import datetime

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from api.supabase_client import supabase


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_food_records(request):
    """List all food consumption records for the current user."""
    try:
        user_id = str(request.user.id)
        params = {
            'id_user': f'eq.{user_id}',
            'order': 'tanggal.desc',
        }

        date_from = request.query_params.get('date_from')
        date_to = request.query_params.get('date_to')
        if date_from:
            params['tanggal'] = f'gte.{date_from}'
        if date_to:
            params['tanggal'] = f'lte.{date_to}'

        rows = supabase.select('food_analysis', params)
        return Response(rows)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_food_record(request):
    """Create a new food consumption record."""
    required = ['nama_makanan', 'kalori']
    for field in required:
        if field not in request.data:
            return Response(
                {'error': f'{field} is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )

    record = {
        'id_user': str(request.user.id),
        'nama_makanan': request.data.get('nama_makanan') or request.data.get('food_name'),
        'kalori': request.data.get('kalori') or request.data.get('calories', 0),
        'protein': request.data.get('protein', 0),
        'lemak': request.data.get('lemak') or request.data.get('fat', 0),
        'karbohidrat': request.data.get('karbohidrat') or request.data.get('carbs', 0),
        'gula': request.data.get('gula') or request.data.get('sugar', 0),
        'tanggal': request.data.get('tanggal') or datetime.utcnow().isoformat() + 'Z',
    }

    try:
        result = supabase.insert('food_analysis', record)
        return Response(result, status=status.HTTP_201_CREATED)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_food_record(request, record_id):
    """Get a single food record."""
    try:
        rows = supabase.select('food_analysis', {
            'id_food': f'eq.{record_id}',
            'id_user': f'eq.{request.user.id}',
        })
        if not rows:
            return Response({'error': 'Record not found.'}, status=status.HTTP_404_NOT_FOUND)
        return Response(rows[0])
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_food_record(request, record_id):
    """Delete a food record."""
    try:
        supabase.delete('food_analysis', {
            'id_food': record_id,
            'id_user': str(request.user.id),
        })
        return Response({'message': 'Record deleted.'}, status=status.HTTP_204_NO_CONTENT)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
