import os
from datetime import date, timedelta, datetime
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
import google.generativeai as genai
from api.supabase_client import supabase

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def coachbot_chat(request):
    """
    Endpoint untuk ngobrol dengan NutriCoach AI (Gemini).
    Menerima text dari user, merespons sebagai ahli gizi pintar.
    """
    user_message = request.data.get("message", "")
    if not user_message:
        return Response({"error": "Pesan tidak boleh kosong"}, status=400)

    # Konfigurasi Gemini
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return Response({"error": "Konfigurasi Gemini belum diatur di server"}, status=500)
    
    genai.configure(api_key=api_key)

    try:
        user_id = request.user.id
        # Ambil data profil untuk target kalori
        profile_rows = supabase.select('users', {'id_user': f'eq.{request.user.id}'})
        target_calories = 2000
        if profile_rows:
            p = profile_rows[0]
            w = float(p.get('berat_badan') or 0)
            h = float(p.get('tinggi_badan') or 0)
            a = float(p.get('umur') or 0)
            if w and h and a:
                gender = p.get('jenis_kelamin', 'male')
                bmr = (10 * w + 6.25 * h - 5 * a + 5) if gender == 'male' else (10 * w + 6.25 * h - 5 * a - 161)
                factors = {'sedentary': 1.2, 'light': 1.375, 'moderate': 1.55, 'active': 1.725, 'veryActive': 1.9}
                tdee = bmr * factors.get(p.get('aktivitas_harian', 'moderate'), 1.55)
                goal = p.get('goal', 'maintain')
                if goal == 'lose': tdee -= 400
                elif goal == 'gain': tdee += 400
                target_calories = round(tdee)
        
        # Ambil makanan hari ini (WIB)
        now_utc = datetime.utcnow()
        today_wib = (now_utc + timedelta(hours=7)).strftime('%Y-%m-%d')
        yesterday_utc = (now_utc - timedelta(days=1)).isoformat()
        
        # Ambil dari 1 hari yang lalu (UTC) agar aman dari pergeseran jam
        food_rows = supabase.select('food_analysis', {
            'id_user': f'eq.{user_id}',
            'tanggal': f'gte.{yesterday_utc}',
        })
        
        # Hitung total nutrisi hari ini berdasarkan timezone WIB
        total_cal = 0
        total_protein = 0
        total_carbs = 0
        total_fat = 0
        for f in food_rows:
            t = f.get('tanggal', '')
            clean_str = t.split('+')[0].replace('Z', '')
            if clean_str:
                dt_local = datetime.fromisoformat(clean_str) + timedelta(hours=7)
                if dt_local.strftime('%Y-%m-%d') == today_wib:
                    total_cal += float(f.get('kalori') or 0)
                    total_protein += float(f.get('protein') or 0)
                    total_carbs += float(f.get('karbohidrat') or 0)
                    total_fat += float(f.get('lemak') or 0)
        
        nutrition_context = f"""
        [DATA NUTRISI PENGGUNA HARI INI]
        - Target Kalori Harian (BMR): {target_calories} kkal
        - Kalori Terkonsumsi: {total_cal} kkal
        - Protein: {total_protein} g
        - Karbohidrat: {total_carbs} g
        - Lemak: {total_fat} g
        Jika pengguna bertanya soal "analisis nutrisi hari ini" atau konsumsi mereka, JAWAB BERDASARKAN DATA INI.
        Beritahu mereka apa yang kurang atau berlebih.
        """

        model = genai.GenerativeModel("gemini-2.5-flash")
        
        # System prompt untuk mengatur persona Gemini
        system_prompt = f"""
        Anda adalah "NutriCoach AI", asisten pintar untuk aplikasi kesehatan bernama Jimamet 2.0. 
        Tugas Anda adalah menjawab pertanyaan pengguna seputar gizi, kalori, diet, dan kesehatan dengan gaya yang ramah, ringkas, informatif, dan empatik.
        Gunakan bahasa Indonesia. Tambahkan emoji agar terkesan ramah. 
        Jangan memberikan resep medis, tapi berikan saran pola makan sehat secara umum.
        Jika pengguna membicarakan gejala medis berat atau penyakit kronis (diabetes, jantung, dll), sarankan mereka untuk menggunakan fitur "Konsultasi Ahli Gizi".
        Usahakan panjang jawaban tidak lebih dari 150 kata (singkat dan padat).
        
        {nutrition_context}
        """
        
        full_prompt = f"{system_prompt}\n\nPesan pengguna: {user_message}\n\nJawaban Anda:"
        
        response = model.generate_content(full_prompt)
        ai_reply = response.text.strip()
        
        # Deteksi otomatis di backend jika perlu konsultasi (opsional tambahan keamanan)
        triggers = ["diabetes", "hipertensi", "darah tinggi", "kolesterol", "hamil", "menyusui", "obesitas", "penyakit", "ginjal", "jantung", "kanker", "asam urat"]
        needs_consultation = any(t in user_message.lower() for t in triggers)

        return Response({
            "reply": ai_reply,
            "needs_consultation": needs_consultation
        }, status=200)

    except Exception as e:
        return Response({"error": str(e)}, status=500)
