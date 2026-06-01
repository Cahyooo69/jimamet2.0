"""
Business logic for NutriCoach AI predictions (Gemini / OpenRouter).
Session listings and details are cached for 30 seconds.
"""

import os
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

import requests
import google.genai as genai
from google.genai import types as genai_types

from api.models import UserModel, FoodRecordModel, CoachSessionModel, CoachMessageModel
from api import cache as app_cache

# Consultation trigger keywords
_CONSULTATION_TRIGGERS = [
    "diabetes",
    "hipertensi",
    "darah tinggi",
    "kolesterol",
    "hamil",
    "menyusui",
    "obesitas",
    "penyakit",
    "ginjal",
    "jantung",
    "kanker",
    "asam urat",
]

_SYSTEM_PROMPT_TEMPLATE = """
Anda adalah "NutriCoach AI", asisten pintar untuk aplikasi kesehatan bernama Jimamet 2.0. 
Tugas Anda adalah menjawab pertanyaan pengguna seputar gizi, kalori, diet, dan kesehatan dengan gaya yang ramah, ringkas, informatif, dan empatik.
Gunakan bahasa Indonesia. Tambahkan emoji agar terkesan ramah. 
Jangan memberikan resep medis, tapi berikan saran pola makan sehat secara umum.
Jika pengguna membicarakan gejala medis berat atau penyakit kronis (diabetes, jantung, dll), sarankan mereka untuk menggunakan fitur "Konsultasi Ahli Gizi".
Usahakan panjang jawaban tidak lebih dari 150 kata (singkat dan padat).

{nutrition_context}
"""


class PredictionService:
    """NutriCoach AI chat business logic."""

    @classmethod
    def list_sessions(cls, user_id: int) -> list:
        """Fetch all sessions for user (cached 30s)."""
        cache_key = app_cache.key_coach_sessions(user_id)
        cached = app_cache.get(cache_key)
        if cached is not None:
            return cached
        result = CoachSessionModel.find_by_user(user_id)
        app_cache.set(cache_key, result, app_cache.TTL_COACH_SESSIONS)
        return result

    @classmethod
    def create_session(cls, user_id: int, title: str = "New Consultation") -> dict:
        """Create a new AI chat session. Invalidates session list cache."""
        result = CoachSessionModel.create({
            "user_id": user_id,
            "title": title
        })
        app_cache.delete(app_cache.key_coach_sessions(user_id))
        return result

    @classmethod
    def get_session(cls, user_id: int, session_id: str) -> dict:
        """Get session details and all its messages (cached 30s)."""
        cache_key = app_cache.key_coach_session_detail(session_id)
        cached = app_cache.get(cache_key)
        if cached is not None:
            return cached

        session = CoachSessionModel.find_by_id_and_user(session_id, user_id)
        if not session:
            raise ValueError("Session not found")

        messages = CoachMessageModel.find_by_session(session_id)
        result = {"session": session, "messages": messages}
        app_cache.set(cache_key, result, app_cache.TTL_COACH_MESSAGES)
        return result

    @classmethod
    def delete_session(cls, user_id: int, session_id: str) -> bool:
        """Delete an AI chat session. Invalidates caches."""
        session = CoachSessionModel.find_by_id_and_user(session_id, user_id)
        if not session:
            raise ValueError("Session not found")

        result = CoachSessionModel.delete(session_id)
        app_cache.delete(app_cache.key_coach_sessions(user_id))
        app_cache.delete(app_cache.key_coach_session_detail(session_id))
        return result

    @classmethod
    def chat(cls, user_id, session_id: str, message: str) -> dict:
        """
        Process a chat message within a session and return AI response.
        """
        if not message:
            raise ValueError("Pesan tidak boleh kosong")
            
        session = CoachSessionModel.find_by_id_and_user(session_id, user_id)
        if not session:
            raise ValueError("Session not found")

        # Update title if it's the first message
        messages = CoachMessageModel.find_by_session(session_id)
        if not messages or (len(messages) == 1 and session["title"] == "New Consultation"):
            title = message[:40] + ("..." if len(message) > 40 else "")
            CoachSessionModel.update(session_id, {"title": title})

        # Build nutrition context
        nutrition = cls._build_nutrition_context(user_id)
        nutrition_context = f"""
        [PROFIL PENGGUNA]
        - Berat Badan: {nutrition['weight']} kg
        - Tinggi Badan: {nutrition['height']} cm
        - Usia: {nutrition['age']} tahun
        - Jenis Kelamin: {nutrition['gender']}
        - Tingkat Aktivitas: {nutrition['activity_level']}
        - Target Kesehatan: {nutrition['goal']}

        [KEBUTUHAN & KONSUMSI HARI INI]
        - Kebutuhan Kalori Harian (TDEE): {nutrition['target_calories']} kkal
        - Kalori Sudah Terkonsumsi: {nutrition['total_cal']} kkal
        - Sisa Kalori: {nutrition['target_calories'] - nutrition['total_cal']} kkal
        - Protein: {nutrition['total_protein']} g
        - Karbohidrat: {nutrition['total_carbs']} g
        - Lemak: {nutrition['total_fat']} g

        INSTRUKSI PENTING:
        - Jika pengguna bertanya tentang kebutuhan kalori, TDEE, BMR, atau target hariannya, JAWAB LANGSUNG dengan angka {nutrition['target_calories']} kkal berdasarkan data profil di atas.
        - Jika pengguna bertanya soal "analisis nutrisi hari ini" atau konsumsi mereka, jawab berdasarkan data konsumsi di atas dan beritahu apa yang kurang atau berlebih.
        - Selalu sebutkan angka spesifik dari data di atas, jangan menjawab secara umum.
        """

        system_prompt = _SYSTEM_PROMPT_TEMPLATE.format(nutrition_context=nutrition_context)
        
        # Build chat history context
        history_context = ""
        for msg in messages[-5:]:  # Last 5 messages for context
            role = "AI" if msg["sender"] == "ai" else "User"
            history_context += f"{role}: {msg['message']}\n"
            
        full_prompt = f"{system_prompt}\n\nRiwayat percakapan:\n{history_context}\n\nPesan pengguna: {message}\n\nJawaban Anda:"

        # Try Gemini first, fallback to OpenRouter
        ai_reply = None
        fallback_error = ""

        api_key = os.environ.get("GEMINI_API_KEY")
        if api_key:
            ai_reply = cls._call_gemini(full_prompt, api_key)
            if not ai_reply:
                fallback_error = "Gemini gagal merespons."
        else:
            fallback_error = "GEMINI_API_KEY tidak diatur."

        if not ai_reply:
            openrouter_key = os.environ.get("OPENROUTER_API_KEY")
            if not openrouter_key:
                raise RuntimeError(f"{fallback_error} | OpenRouter juga tidak bisa digunakan " f"karena OPENROUTER_API_KEY belum diatur.")
            
            # Send simplified prompt to OpenRouter
            or_prompt = f"{system_prompt}\n\nRiwayat percakapan:\n{history_context}"
            ai_reply = cls._call_openrouter(or_prompt, message, openrouter_key)
            if not ai_reply:
                raise RuntimeError(f"{fallback_error} | OpenRouter juga gagal merespons.")

        # Append disclaimer footer
        ai_reply += "\n\nRekomendasi ini berdasarkan data konsumsi dan goal kamu. Untuk kondisi kesehatan khusus, disarankan konsultasi dengan Nutritionist."

        # Check if consultation is needed
        needs_consultation = any(t in message.lower() for t in _CONSULTATION_TRIGGERS)

        # Save to database
        CoachMessageModel.create({
            "session_id": session_id,
            "sender": "user", 
            "message": message
        })
        CoachMessageModel.create({
            "session_id": session_id,
            "sender": "ai", 
            "message": ai_reply,
            "needs_consultation": needs_consultation
        })
        
        # Update session updated_at
        updated_session = CoachSessionModel.update(session_id, {"updated_at": datetime.utcnow().isoformat() + "Z"})

        # Invalidate caches
        app_cache.delete(app_cache.key_coach_sessions(user_id))
        app_cache.delete(app_cache.key_coach_session_detail(session_id))

        return {
            "reply": ai_reply, 
            "needs_consultation": needs_consultation,
            "session": updated_session
        }

    @classmethod
    def _build_nutrition_context(cls, user_id) -> dict:
        """Gather user profile and today's nutrition data."""
        target_calories = 2000

        profile = UserModel.find_by_id(user_id)
        if profile:
            w = float(profile.get("weight") or 0)
            h = float(profile.get("height") or 0)
            a = float(profile.get("age") or 0)
            if w and h and a:
                gender = profile.get("gender", "male")
                bmr = (10 * w + 6.25 * h - 5 * a + 5) if gender == "male" else (10 * w + 6.25 * h - 5 * a - 161)
                factors = {
                    "sedentary": 1.2,
                    "light": 1.375,
                    "moderate": 1.55,
                    "active": 1.725,
                    "veryActive": 1.9,
                }
                tdee = bmr * factors.get(profile.get("activity_level", "moderate"), 1.55)
                goal = profile.get("goal", "maintain")
                if goal == "lose":
                    tdee -= 400
                elif goal == "gain":
                    tdee += 400
                target_calories = round(tdee)

        # Get today's food records (WIB timezone)
        now_utc = datetime.utcnow()
        today_wib = (now_utc + timedelta(hours=7)).strftime("%Y-%m-%d")
        yesterday_utc = (now_utc - timedelta(days=1)).isoformat()

        food_rows = FoodRecordModel.find_by_user(
            user_id,
            order="recorded_at.desc",
            extra_params={"recorded_at": f"gte.{yesterday_utc}"},
        )

        total_cal = 0
        total_protein = 0
        total_carbs = 0
        total_fat = 0
        for f in food_rows:
            t = f.get("recorded_at", "")
            clean_str = t.split("+")[0].replace("Z", "")
            if clean_str:
                dt_local = datetime.fromisoformat(clean_str) + timedelta(hours=7)
                if dt_local.strftime("%Y-%m-%d") == today_wib:
                    total_cal += float(f.get("calories") or 0)
                    total_protein += float(f.get("protein") or 0)
                    total_carbs += float(f.get("carbs") or 0)
                    total_fat += float(f.get("fat") or 0)

        return {
            "weight": profile.get("weight", "—") if profile else "—",
            "height": profile.get("height", "—") if profile else "—",
            "age": profile.get("age", "—") if profile else "—",
            "gender": "Laki-laki" if (profile or {}).get("gender", "male") == "male" else "Perempuan",
            "activity_level": {
                "sedentary": "Tidak aktif",
                "light": "Ringan",
                "moderate": "Sedang",
                "active": "Aktif",
                "veryActive": "Sangat Aktif",
            }.get((profile or {}).get("activity_level", "moderate"), "Sedang"),
            "goal": {
                "lose": "Turunkan Berat",
                "maintain": "Pertahankan",
                "gain": "Naikkan Berat",
            }.get((profile or {}).get("goal", "maintain"), "Pertahankan"),
            "target_calories": target_calories,
            "total_cal": total_cal,
            "total_protein": total_protein,
            "total_carbs": total_carbs,
            "total_fat": total_fat,
        }

    @classmethod
    def _call_gemini(cls, full_prompt: str, api_key: str) -> str | None:
        """Call Gemini API directly. Returns response text or None."""
        try:
            client = genai.Client(api_key=api_key)
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=full_prompt,
            )
            return response.text.strip()
        except Exception as e:
            logger.error("[Gemini ERROR] %s: %s", type(e).__name__, e)
            return None

    @classmethod
    def _call_openrouter(cls, system_prompt: str, user_message: str, api_key: str) -> str | None:
        """Fallback to OpenRouter API. Returns response text or None."""
        try:
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            }
            data = {
                "model": "google/gemini-2.5-flash",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message},
                ],
            }
            resp = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=data,
                timeout=15,
            )
            resp.raise_for_status()
            return resp.json()["choices"][0]["message"]["content"].strip()
        except Exception as e:
            logger.error("[OpenRouter ERROR] %s: %s", type(e).__name__, e)
            return None
