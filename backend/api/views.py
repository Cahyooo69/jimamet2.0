"""
Jimamet Medical Nutrition Platform — API Views.
Endpoints: Auth, User Profile, Food Consumption History.
"""

from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .supabase_client import supabase


# ═══════════════════════════════════════════════════
#  HEALTH CHECK
# ═══════════════════════════════════════════════════

@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """Health check endpoint."""
    return Response({
        'status': 'ok',
        'service': 'Jimamet Medical Nutrition API',
        'version': '1.0.0',
    })


# ═══════════════════════════════════════════════════
#  AUTH — Register / Login / Logout / Me
# ═══════════════════════════════════════════════════

@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    """Register a new user with Django auth + create Supabase profile."""
    username = request.data.get('username')
    email = request.data.get('email')
    password = request.data.get('password')
    full_name = request.data.get('full_name', '')

    if not username or not email or not password:
        return Response(
            {'error': 'Username, email, and password are required.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    if User.objects.filter(username=username).exists():
        return Response(
            {'error': 'Username already exists.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    if User.objects.filter(email=email).exists():
        return Response(
            {'error': 'Email already registered.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    name_parts = full_name.split(' ', 1)
    user = User.objects.create_user(
        username=username,
        email=email,
        password=password,
        first_name=name_parts[0] if name_parts else '',
        last_name=name_parts[1] if len(name_parts) > 1 else '',
    )

    try:
        supabase.insert('users', {
            'id_user': user.id,
            'nama': full_name,
            'email': email,
            'password': password,
            'umur': request.data.get('age', None),
            'berat_badan': request.data.get('weight', None),
            'tinggi_badan': request.data.get('height', None),
            'aktivitas_harian': request.data.get('activity_level', 'moderate'),
        })
    except Exception as e:
        print(f'[Supabase] Profile create warning: {e}')

    # Create auth token
    token, _ = Token.objects.get_or_create(user=user)

    return Response({
        'message': 'Registration successful.',
        'token': token.key,
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'full_name': user.get_full_name(),
        }
    }, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([AllowAny])
def login_user(request):
    """Login with Django auth."""
    username = request.data.get('username')
    password = request.data.get('password')

    if not username or not password:
        return Response(
            {'error': 'Username and password are required.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # 1. Check ahli_gizi table first (before Django auth)
    try:
        ahli_rows = supabase.select('ahli_gizi', {'username': f'eq.{username}'})
        if ahli_rows:
            ag = ahli_rows[0]
            # Simple password check (plaintext stored in Supabase for ahli gizi)
            if ag.get('password') == password:
                return Response({
                    'message': 'Login successful.',
                    'token': f'ahligizi_{ag["id_ahli_gizi"]}',  # pseudo-token
                    'role': 'ahli_gizi',
                    'user': {
                        'id': ag['id_ahli_gizi'],
                        'username': ag['username'],
                        'email': ag.get('email', ''),
                        'full_name': ag.get('nama', ''),
                        'spesialisasi': ag.get('spesialisasi', ''),
                        'no_str': ag.get('no_str', ''),
                    }
                })
    except Exception as e:
        print(f'[AhliGizi] Login check error: {e}')

    # 2. Django auth for regular users
    user = authenticate(request, username=username, password=password)
    if user is not None:
        token, _ = Token.objects.get_or_create(user=user)
        return Response({
            'message': 'Login successful.',
            'token': token.key,
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'full_name': user.get_full_name(),
            }
        })
    else:
        return Response(
            {'error': 'Invalid credentials.'},
            status=status.HTTP_401_UNAUTHORIZED
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_user(request):
    """Logout user — deletes the auth token."""
    try:
        request.user.auth_token.delete()
    except Exception:
        pass
    return Response({'message': 'Logout successful.'})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_current_user(request):
    """Get current authenticated user info."""
    user = request.user
    return Response({
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'full_name': user.get_full_name(),
    })


# ═══════════════════════════════════════════════════
#  USER PROFILE (Supabase)
# ═══════════════════════════════════════════════════

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
            # Map back to English for frontend
            return Response({
                'user_id': request.user.id,
                'full_name': row.get('nama'),
                'email': row.get('email'),
                'username': request.user.username,
                'age': row.get('umur'),
                'weight': row.get('berat_badan'),
                'height': row.get('tinggi_badan'),
                'gender': 'male',
                'activity_level': row.get('aktivitas_harian', 'moderate'),
                'goal': 'maintain',
            })
        else:
            # Return default profile
            return Response({
                'user_id': request.user.id,
                'full_name': request.user.get_full_name(),
                'email': request.user.email,
                'username': request.user.username,
                'age': None,
                'weight': None,
                'height': None,
                'gender': 'male',
                'activity_level': 'moderate',
                'goal': 'maintain',
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
        # Check if profile exists
        rows = supabase.select('users', {'email': f'eq.{request.user.email}'})
        
        # Map English to Indonesian
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
            # Create if doesn't exist
            mapped_data['email'] = request.user.email
            mapped_data['id_user'] = request.user.id
            if 'nama' not in mapped_data: mapped_data['nama'] = request.user.get_full_name()
            result = supabase.insert('users', mapped_data)

        # Also update Django user if full_name changed
        if 'full_name' in update_data:
            parts = update_data['full_name'].split(' ', 1)
            request.user.first_name = parts[0]
            request.user.last_name = parts[1] if len(parts) > 1 else ''
            request.user.save()

        return Response(result)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ═══════════════════════════════════════════════════
#  FOOD CONSUMPTION HISTORY (Supabase)
# ═══════════════════════════════════════════════════

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_food_records(request):
    """List all food consumption records for the current user."""
    try:
        params = {
            'user_id': f'eq.{request.user.id}',
            'order': 'consumed_at.desc',
        }

        # Optional date filter
        date_from = request.query_params.get('date_from')
        date_to = request.query_params.get('date_to')
        if date_from:
            params['consumed_at'] = f'gte.{date_from}'
        if date_to:
            params['consumed_at'] = f'lte.{date_to}'

        rows = supabase.select('food_records', params)
        return Response(rows)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_food_record(request):
    """Create a new food consumption record."""
    required = ['food_name', 'calories']
    for field in required:
        if field not in request.data:
            return Response(
                {'error': f'{field} is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )

    record = {
        'user_id': request.user.id,
        'food_name': request.data.get('food_name'),
        'emoji': request.data.get('emoji', '🍽️'),
        'calories': request.data.get('calories'),
        'protein': request.data.get('protein', 0),
        'carbs': request.data.get('carbs', 0),
        'fat': request.data.get('fat', 0),
        'fiber': request.data.get('fiber', 0),
        'sugar': request.data.get('sugar', 0),
        'sodium': request.data.get('sodium', 0),
        'portion': request.data.get('portion', '1 porsi'),
        'consumed_at': request.data.get('consumed_at'),  # ISO timestamp
        'confidence': request.data.get('confidence'),
        'image_url': request.data.get('image_url'),
        'tags': request.data.get('tags', []),
        'recommendation': request.data.get('recommendation', ''),
    }

    try:
        result = supabase.insert('food_records', record)
        return Response(result, status=status.HTTP_201_CREATED)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_food_record(request, record_id):
    """Get a single food record."""
    try:
        rows = supabase.select('food_records', {
            'id': f'eq.{record_id}',
            'user_id': f'eq.{request.user.id}',
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
        supabase.delete('food_records', {
            'id': record_id,
            'user_id': request.user.id,
        })
        return Response({'message': 'Record deleted.'}, status=status.HTTP_204_NO_CONTENT)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ═══════════════════════════════════════════════════
#  DASHBOARD SUMMARY
# ═══════════════════════════════════════════════════

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_summary(request):
    """Get daily nutrition summary for dashboard."""
    from datetime import date

    today = request.query_params.get('date', date.today().isoformat())

    try:
        rows = supabase.select('food_records', {
            'user_id': f'eq.{request.user.id}',
            'consumed_at': f'gte.{today}T00:00:00',
        })

        total_cal = sum(r.get('calories', 0) or 0 for r in rows)
        total_protein = sum(r.get('protein', 0) or 0 for r in rows)
        total_carbs = sum(r.get('carbs', 0) or 0 for r in rows)
        total_fat = sum(r.get('fat', 0) or 0 for r in rows)
        total_fiber = sum(r.get('fiber', 0) or 0 for r in rows)

        return Response({
            'date': today,
            'total_meals': len(rows),
            'total_calories': total_cal,
            'total_protein': total_protein,
            'total_carbs': total_carbs,
            'total_fat': total_fat,
            'total_fiber': total_fiber,
            'meals': rows,
        })
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ═══════════════════════════════════════════════════
#  KONSULTASI (Rujukan CoachBot → Ahli Gizi)
# ═══════════════════════════════════════════════════

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_konsultasi(request):
    """User (CoachBot) membuat permintaan konsultasi ke ahli gizi."""
    pesan = request.data.get('pesan_coachbot', '')
    if not pesan:
        return Response({'error': 'pesan_coachbot is required.'}, status=400)
    try:
        res = supabase.insert('konsultasi', {
            'id_user': str(request.user.id),
            'pesan_coachbot': pesan,
            'status': 'menunggu',
            'catatan_ahli_gizi': '',
        })
        return Response(res, status=201)
    except Exception as e:
        return Response({'error': str(e)}, status=500)


@api_view(['GET'])
@authentication_classes([])
@permission_classes([AllowAny])
def list_konsultasi(request):
    """Ahli gizi melihat semua daftar konsultasi yang masuk."""
    try:
        rows = supabase.select('konsultasi', {'order': 'tanggal.desc'})
        result = []
        for r in rows:
            # Ambil nama user dari tabel users
            user_rows = supabase.select('users', {'id_user': f"eq.{r['id_user']}"})
            user_info = user_rows[0] if user_rows else {}
            result.append({
                'id_konsultasi': r.get('id_konsultasi'),
                'id_user': r.get('id_user'),
                'nama_pasien': user_info.get('nama', 'Unknown'),
                'email_pasien': user_info.get('email', ''),
                'pesan_coachbot': r.get('pesan_coachbot'),
                'status': r.get('status'),
                'catatan_ahli_gizi': r.get('catatan_ahli_gizi', ''),
                'tanggal': r.get('tanggal'),
            })
        return Response(result)
    except Exception as e:
        return Response({'error': str(e)}, status=500)


@api_view(['PATCH'])
@authentication_classes([])
@permission_classes([AllowAny])
def update_konsultasi(request, konsultasi_id):
    """Ahli gizi mengupdate status & catatan konsultasi."""
    update_data = {}
    if 'status' in request.data:
        update_data['status'] = request.data['status']
    if 'catatan_ahli_gizi' in request.data:
        update_data['catatan_ahli_gizi'] = request.data['catatan_ahli_gizi']
    if not update_data:
        return Response({'error': 'No fields to update.'}, status=400)
    try:
        res = supabase.update('konsultasi', {'id_konsultasi': konsultasi_id}, update_data)
        return Response(res)
    except Exception as e:
        return Response({'error': str(e)}, status=500)


@api_view(['DELETE'])
@authentication_classes([])
@permission_classes([AllowAny])
def delete_konsultasi(request, konsultasi_id):
    """Ahli gizi menghapus sesi konsultasi."""
    try:
        supabase.delete('konsultasi', {'id_konsultasi': konsultasi_id})
        return Response({'message': 'Konsultasi deleted successfully.'}, status=200)
    except Exception as e:
        return Response({'error': str(e)}, status=500)


# ═══════════════════════════════════════════════════
#  CHAT KONSULTASI (User ↔ Ahli Gizi)
# ═══════════════════════════════════════════════════

@api_view(['GET'])
@authentication_classes([])
@permission_classes([AllowAny])
def list_chat(request, konsultasi_id):
    """Ambil semua pesan chat untuk satu sesi konsultasi."""
    try:
        rows = supabase.select('chat_konsultasi', {
            'id_konsultasi': f'eq.{konsultasi_id}',
            'order': 'tanggal.asc'
        })
        return Response(rows)
    except Exception as e:
        return Response({'error': str(e)}, status=500)


@api_view(['POST'])
@authentication_classes([])
@permission_classes([AllowAny])
def send_chat(request, konsultasi_id):
    """Kirim pesan chat. pengirim: 'user' atau 'ahli_gizi'."""
    pesan = request.data.get('pesan', '').strip()
    pengirim = request.data.get('pengirim', 'user')
    if not pesan:
        return Response({'error': 'pesan tidak boleh kosong.'}, status=400)
    if pengirim not in ('user', 'ahli_gizi'):
        return Response({'error': 'pengirim harus user atau ahli_gizi.'}, status=400)
    try:
        # Pastikan konsultasi ada
        k = supabase.select('konsultasi', {'id_konsultasi': f'eq.{konsultasi_id}'})
        if not k:
            return Response({'error': 'Konsultasi tidak ditemukan.'}, status=404)
        res = supabase.insert('chat_konsultasi', {
            'id_konsultasi': konsultasi_id,
            'pengirim': pengirim,
            'pesan': pesan,
        })
        return Response(res, status=201)
    except Exception as e:
        return Response({'error': str(e)}, status=500)


@api_view(['DELETE'])
@authentication_classes([])
@permission_classes([AllowAny])
def delete_chat(request, chat_id):
    """Hapus pesan chat."""
    try:
        supabase.delete('chat_konsultasi', {'id_chat': chat_id})
        return Response({'message': 'Chat deleted successfully.'}, status=200)
    except Exception as e:
        return Response({'error': str(e)}, status=500)

