"""
Profile views: get and update user profile.
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from api.supabase_client import supabase


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_profile(request):
    """Get the current user's profile from Supabase."""
    try:
        rows = supabase.select('users', {
            'email': f'eq.{request.user.email}',
        })
        if rows:
            row = rows[0]
            return Response({
                'user_id': request.user.id,
                'full_name': row.get('nama'),
                'email': row.get('email'),
                'username': request.user.username,
                'age': row.get('umur'),
                'weight': row.get('berat_badan'),
                'height': row.get('tinggi_badan'),
                'gender': row.get('jenis_kelamin'),
                'activity_level': row.get('aktivitas_harian', 'moderate'),
                'goal': row.get('goal'),
            })
        else:
            return Response({
                'user_id': request.user.id,
                'full_name': request.user.get_full_name(),
                'email': request.user.email,
                'username': request.user.username,
                'age': None,
                'weight': None,
                'height': None,
                'gender': None,
                'activity_level': 'moderate',
                'goal': None,
            })
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def update_profile(request):
    """Update the current user's profile in Supabase."""
    allowed_fields = [
        'full_name', 'age', 'weight', 'height',
        'gender', 'activity_level', 'goal',
    ]
    update_data = {k: v for k, v in request.data.items() if k in allowed_fields}

    if not update_data:
        return Response({'error': 'No valid fields to update.'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        rows = supabase.select('users', {'email': f'eq.{request.user.email}'})

        mapped_data = {}
        if 'full_name' in update_data: mapped_data['nama'] = update_data['full_name']
        if 'age' in update_data: mapped_data['umur'] = update_data['age']
        if 'weight' in update_data: mapped_data['berat_badan'] = update_data['weight']
        if 'height' in update_data: mapped_data['tinggi_badan'] = update_data['height']
        if 'activity_level' in update_data: mapped_data['aktivitas_harian'] = update_data['activity_level']

        if rows:
            if mapped_data:
                result = supabase.update(
                    'users',
                    {'email': request.user.email},
                    mapped_data,
                )
        else:
            mapped_data['email'] = request.user.email
            mapped_data['id_user'] = request.user.id
            if 'nama' not in mapped_data: mapped_data['nama'] = request.user.get_full_name()
            result = supabase.insert('users', mapped_data)

        if 'full_name' in update_data:
            parts = update_data['full_name'].split(' ', 1)
            request.user.first_name = parts[0]
            request.user.last_name = parts[1] if len(parts) > 1 else ''
            request.user.save()

        return Response(result)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
