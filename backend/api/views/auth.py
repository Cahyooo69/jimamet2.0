"""
Auth views: register, login, logout, me.
"""

from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password, check_password
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from api.supabase_client import supabase


@api_view(["GET"])
@permission_classes([AllowAny])
def health_check(request):
    """Health check endpoint."""
    return Response(
        {
            "status": "ok",
            "service": "Jimamet Medical Nutrition API",
            "version": "1.0.0",
        }
    )


@api_view(["POST"])
@permission_classes([AllowAny])
def register_user(request):
    """Register a new user with Django auth + create Supabase profile."""
    username = request.data.get("username")
    email = request.data.get("email")
    password = request.data.get("password")
    full_name = request.data.get("full_name", "")

    if not username or not email or not password:
        return Response({"error": "Username, email, and password are required."}, status=status.HTTP_400_BAD_REQUEST)

    if User.objects.filter(username=username).exists():
        return Response({"error": "Username already exists."}, status=status.HTTP_400_BAD_REQUEST)

    if User.objects.filter(email=email).exists():
        return Response({"error": "Email already registered."}, status=status.HTTP_400_BAD_REQUEST)

    name_parts = full_name.split(" ", 1)
    user = User.objects.create_user(
        username=username,
        email=email,
        password=password,
        first_name=name_parts[0] if name_parts else "",
        last_name=name_parts[1] if len(name_parts) > 1 else "",
    )

    try:
        supabase.insert(
            "users",
            {
                "id_user": user.id,
                "nama": full_name,
                "email": email,
                "password": make_password(password),
                "umur": request.data.get("age", None),
                "berat_badan": request.data.get("weight", None),
                "tinggi_badan": request.data.get("height", None),
                "aktivitas_harian": request.data.get("activity_level", "moderate"),
            },
        )
    except Exception:
        pass  # Profil Supabase gagal dibuat, akun Django tetap valid

    token, _ = Token.objects.get_or_create(user=user)

    return Response(
        {
            "message": "Registration successful.",
            "token": token.key,
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "full_name": user.get_full_name(),
            },
        },
        status=status.HTTP_201_CREATED,
    )


@api_view(["POST"])
@permission_classes([AllowAny])
def login_user(request):
    """Login with Django auth."""
    username = request.data.get("username")
    password = request.data.get("password")

    if not username or not password:
        return Response({"error": "Username and password are required."}, status=status.HTTP_400_BAD_REQUEST)

    # 1. Check ahli_gizi table first (before Django auth)
    try:
        ahli_rows = supabase.select("ahli_gizi", {"username": f"eq.{username}"})
        if ahli_rows:
            ag = ahli_rows[0]
            stored_pw = ag.get("password")
            if check_password(password, stored_pw) or stored_pw == password:
                # Upgrade legacy plain-text password to hashed password on successful login
                if stored_pw == password and not stored_pw.startswith("pbkdf2_") and not stored_pw.startswith("bcrypt"):
                    try:
                        supabase.update("ahli_gizi", {"id_ahli_gizi": ag["id_ahli_gizi"]}, {"password": make_password(password)})
                    except Exception:
                        pass
                return Response(
                    {
                        "message": "Login successful.",
                        "token": f'ahligizi_{ag["id_ahli_gizi"]}',
                        "role": "ahli_gizi",
                        "user": {
                            "id": ag["id_ahli_gizi"],
                            "username": ag["username"],
                            "email": ag.get("email", ""),
                            "full_name": ag.get("nama", ""),
                            "spesialisasi": ag.get("spesialisasi", ""),
                            "no_str": ag.get("no_str", ""),
                        },
                    }
                )
    except Exception:
        pass  # Tabel ahli_gizi tidak dapat diakses, lanjut ke Django auth

    # 2. Django auth for regular users
    user = authenticate(request, username=username, password=password)
    if user is not None:
        # Check if the user data still exists in Supabase
        try:
            sb_users = supabase.select("users", {"id_user": f"eq.{user.id}"})
            if not sb_users:
                # User no longer exists in Supabase, deny login and clean up local user
                user.delete()
                return Response({"error": "Invalid credentials."}, status=status.HTTP_401_UNAUTHORIZED)
        except Exception:
            pass  # Fallback: if Supabase check fails due to network, proceed as usual

        token, _ = Token.objects.get_or_create(user=user)
        return Response(
            {
                "message": "Login successful.",
                "token": token.key,
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "full_name": user.get_full_name(),
                },
            }
        )
    else:
        return Response({"error": "Invalid credentials."}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout_user(request):
    """Logout user — deletes the auth token."""
    try:
        request.user.auth_token.delete()
    except Exception:
        pass
    return Response({"message": "Logout successful."})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_current_user(request):
    """Get current authenticated user info."""
    user = request.user
    return Response(
        {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "full_name": user.get_full_name(),
        }
    )
