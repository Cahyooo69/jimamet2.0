"""
Jimamet Medical Nutrition Platform — API Views.
Endpoints: Auth, User Profile, Food Consumption History.
"""

from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
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

    # Create profile in Supabase
    try:
        supabase.insert('user_profiles', {
            'user_id': user.id,
            'full_name': full_name,
            'email': email,
            'username': username,
            'age': None,
            'weight': None,
            'height': None,
            'gender': 'male',
            'activity_level': 'moderate',
            'goal': 'maintain',
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
        rows = supabase.select('user_profiles', {
            'user_id': f'eq.{request.user.id}',
        })
        if rows:
            return Response(rows[0])
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
        rows = supabase.select('user_profiles', {'user_id': f'eq.{request.user.id}'})
        if rows:
            result = supabase.update(
                'user_profiles',
                {'user_id': request.user.id},
                update_data,
            )
        else:
            # Create if doesn't exist
            update_data['user_id'] = request.user.id
            update_data['email'] = request.user.email
            update_data['username'] = request.user.username
            result = supabase.insert('user_profiles', update_data)

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
