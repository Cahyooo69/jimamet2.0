"""
Konsultasi & Chat views: rujukan CoachBot ke ahli gizi + pesan chat.
"""
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from api.supabase_client import supabase


# ═══════════════════════════════════════════════════
#  KONSULTASI
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
#  CHAT KONSULTASI
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
