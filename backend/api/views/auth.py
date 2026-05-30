"""
Auth views: register, login, logout, me, supabase_webhook.
Semua autentikasi menggunakan Supabase — tidak ada Django User/Token model.
"""
import hmac

from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from api.supabase_client import supabase
from api.supabase_auth import hash_password, verify_password, generate_token


@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """Health check endpoint."""
    return Response({
        'status': 'ok',
        'service': 'Jimamet Medical Nutrition API',
        'version': '2.0.0',
    })


@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    """Register user baru — semua data disimpan ke Supabase."""
    username = request.data.get('username', '').strip()
    email = request.data.get('email', '').strip()
    password = request.data.get('password', '')
    full_name = request.data.get('full_name', '')

    if not username or not email or not password:
        return Response(
            {'error': 'Username, email, dan password wajib diisi.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Cek username duplikat
    try:
        if supabase.select('users', {'id_user': f'eq.{username}'}):
            return Response(
                {'error': 'Username sudah digunakan.'},
                status=status.HTTP_400_BAD_REQUEST
            )
    except Exception as e:
        return Response({'error': f'Gagal cek username: {e}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # Cek email duplikat
    try:
        if supabase.select('users', {'email': f'eq.{email}'}):
            return Response(
                {'error': 'Email sudah terdaftar.'},
                status=status.HTTP_400_BAD_REQUEST
            )
    except Exception as e:
        return Response({'error': f'Gagal cek email: {e}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # Hash password + generate token sesi
    password_hash = hash_password(password)
    token = generate_token()

    try:
        supabase.insert('users', {
            'id_user': username,           # username = primary key
            'nama': full_name,
            'email': email,
            'password': password_hash,
            'token': token,
            'umur': request.data.get('age') or None,
            'berat_badan': request.data.get('weight') or None,
            'tinggi_badan': request.data.get('height') or None,
            'aktivitas_harian': request.data.get('activity_level', 'moderate'),
        })
    except Exception as e:
        return Response({'error': f'Gagal membuat akun: {e}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return Response({
        'message': 'Registrasi berhasil.',
        'token': token,
        'user': {
            'id': username,
            'username': username,
            'email': email,
            'full_name': full_name,
        }
    }, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([AllowAny])
def login_user(request):
    """Login — validasi kredensial dari Supabase."""
    username = request.data.get('username', '').strip()
    password = request.data.get('password', '')

    if not username or not password:
        return Response(
            {'error': 'Username dan password wajib diisi.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # 1. Cek ahli_gizi dulu
    try:
        ahli_rows = supabase.select('ahli_gizi', {'username': f'eq.{username}'})
        if ahli_rows:
            ag = ahli_rows[0]
            if ag.get('password') == password:
                return Response({
                    'message': 'Login berhasil.',
                    'token': f'ahligizi_{ag["id_ahli_gizi"]}',
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
    except Exception:
        pass

    # 2. Cek tabel users di Supabase
    try:
        rows = supabase.select('users', {'id_user': f'eq.{username}'})
    except Exception as e:
        return Response({'error': f'Gagal mengakses database: {e}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    if not rows:
        return Response({'error': 'Username atau password salah.'}, status=status.HTTP_401_UNAUTHORIZED)

    user_row = rows[0]

    if not verify_password(password, user_row.get('password', '')):
        return Response({'error': 'Username atau password salah.'}, status=status.HTTP_401_UNAUTHORIZED)

    # Rotate token setiap login (keamanan)
    new_token = generate_token()
    try:
        supabase.update('users', {'id_user': username}, {'token': new_token})
    except Exception as e:
        return Response({'error': f'Gagal memperbarui token: {e}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return Response({
        'message': 'Login berhasil.',
        'token': new_token,
        'user': {
            'id': username,
            'username': username,
            'email': user_row.get('email', ''),
            'full_name': user_row.get('nama', ''),
        }
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_user(request):
    """Logout — hapus token dari Supabase."""
    user = request.user
    # Ahli gizi tidak punya token di Supabase users table
    if getattr(user, 'role', '') == 'ahli_gizi':
        return Response({'message': 'Logout berhasil.'})

    try:
        supabase.update('users', {'id_user': user.id}, {'token': None})
    except Exception:
        pass
    return Response({'message': 'Logout berhasil.'})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_current_user(request):
    """Get info user yang sedang login."""
    user = request.user
    return Response({
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'full_name': user.get_full_name(),
    })


@api_view(['POST'])
@permission_classes([AllowAny])
def supabase_webhook(request):
    """
    Webhook dari Supabase — dipanggil otomatis saat user dihapus.
    Sekarang hanya logging saja karena tidak ada SQLite yang perlu disync.
    """
    webhook_secret = getattr(settings, 'SUPABASE_WEBHOOK_SECRET', '')
    if webhook_secret:
        incoming_secret = request.headers.get('x-webhook-secret', '')
        if not hmac.compare_digest(incoming_secret, webhook_secret):
            return Response({'error': 'Unauthorized.'}, status=status.HTTP_401_UNAUTHORIZED)

    payload = request.data
    if payload.get('type') == 'DELETE' and payload.get('table') == 'users':
        id_user = payload.get('old_record', {}).get('id_user')
        return Response({'message': f'User {id_user} telah dihapus dari Supabase.'})

    return Response({'message': 'Event diabaikan.'}, status=status.HTTP_200_OK)
