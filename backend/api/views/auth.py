"""
Auth views: register, login, logout, me, supabase_webhook.
"""
import hmac

from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from api.supabase_client import supabase


@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """Health check endpoint."""
    return Response({
        'status': 'ok',
        'service': 'Jimamet Medical Nutrition API',
        'version': '1.0.0',
    })


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

    # Cek username duplikat — tapi jika ada di SQLite & tidak ada di Supabase,
    # itu adalah orphan user (dihapus dari Supabase) → bersihkan otomatis.
    existing_by_username = User.objects.filter(username=username).first()
    if existing_by_username:
        try:
            supabase_check = supabase.select('users', {'id_user': f'eq.{existing_by_username.id}'})
            if supabase_check:
                # Benar-benar masih ada di Supabase → tolak
                return Response(
                    {'error': 'Username sudah digunakan.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            else:
                # Orphan: ada di SQLite tapi tidak di Supabase → hapus dulu
                try:
                    existing_by_username.auth_token.delete()
                except Exception:
                    pass
                existing_by_username.delete()
        except Exception:
            # Supabase tidak bisa diakses → tolak aman
            return Response(
                {'error': 'Username sudah digunakan.'},
                status=status.HTTP_400_BAD_REQUEST
            )

    # Cek email duplikat dengan logika yang sama
    existing_by_email = User.objects.filter(email=email).first()
    if existing_by_email:
        try:
            supabase_check = supabase.select('users', {'id_user': f'eq.{existing_by_email.id}'})
            if supabase_check:
                return Response(
                    {'error': 'Email sudah terdaftar.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            else:
                try:
                    existing_by_email.auth_token.delete()
                except Exception:
                    pass
                existing_by_email.delete()
        except Exception:
            return Response(
                {'error': 'Email sudah terdaftar.'},
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
    except Exception:
        pass  # Profil Supabase gagal dibuat, akun Django tetap valid

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
            if ag.get('password') == password:
                return Response({
                    'message': 'Login successful.',
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
        pass  # Tabel ahli_gizi tidak dapat diakses, lanjut ke Django auth

    # 2. Django auth for regular users
    user = authenticate(request, username=username, password=password)
    if user is not None:
        # 3. Verify user still exists in Supabase (source of truth for user profiles)
        try:
            supabase_rows = supabase.select('users', {'id_user': f'eq.{user.id}'})
            if not supabase_rows:
                # User deleted from Supabase → cascade delete from Django SQLite too
                try:
                    user.auth_token.delete()
                except Exception:
                    pass
                user.delete()
                return Response(
                    {'error': 'Akun tidak ditemukan atau telah dihapus.'},
                    status=status.HTTP_401_UNAUTHORIZED
                )
        except Exception:
            # If Supabase is unreachable, fall through to allow login
            pass

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


@api_view(['POST'])
@permission_classes([AllowAny])
def supabase_webhook(request):
    """
    Endpoint yang dipanggil otomatis oleh Supabase Database Webhook
    saat ada event DELETE pada tabel 'users'.
    Menghapus Django user dari SQLite secara real-time.
    """
    # Verifikasi webhook secret agar tidak sembarang request bisa masuk
    webhook_secret = getattr(settings, 'SUPABASE_WEBHOOK_SECRET', '')
    if webhook_secret:
        incoming_secret = request.headers.get('x-webhook-secret', '')
        if not hmac.compare_digest(incoming_secret, webhook_secret):
            return Response(
                {'error': 'Unauthorized webhook request.'},
                status=status.HTTP_401_UNAUTHORIZED
            )

    payload = request.data
    event_type = payload.get('type', '')   # INSERT | UPDATE | DELETE
    table = payload.get('table', '')

    # Hanya proses event DELETE pada tabel users
    if event_type != 'DELETE' or table != 'users':
        return Response({'message': 'Event ignored.'}, status=status.HTTP_200_OK)

    old_record = payload.get('old_record', {})
    id_user = old_record.get('id_user')

    if not id_user:
        return Response(
            {'error': 'id_user tidak ditemukan di payload.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        django_user = User.objects.get(id=id_user)
        username = django_user.username
        try:
            django_user.auth_token.delete()
        except Exception:
            pass
        django_user.delete()
        return Response({
            'message': f'User "{username}" (id={id_user}) berhasil dihapus dari SQLite.'
        }, status=status.HTTP_200_OK)
    except User.DoesNotExist:
        # Tidak ada di SQLite — tidak perlu aksi
        return Response(
            {'message': f'User id={id_user} tidak ditemukan di SQLite, tidak ada yang dihapus.'},
            status=status.HTTP_200_OK
        )
