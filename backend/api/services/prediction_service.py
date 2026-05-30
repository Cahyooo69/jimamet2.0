"""
Business logic for NutriCoach AI predictions (Gemini / OpenRouter).
"""

import os
from datetime import datetime, timedelta

import requests
import google.generativeai as genai

from api.models import UserModel, FoodAnalysisModel

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
    def chat(cls, user_id, message: str) -> dict:
        """
        Process a chat message and return AI response.

        Returns dict: {reply, needs_consultation}
        Raises ValueError if message is empty.
        Raises RuntimeError if all AI providers fail.
        """
        if not message:
            raise ValueError("Pesan tidak boleh kosong")

        # Build nutrition context
        nutrition = cls._build_nutrition_context(user_id)
        nutrition_context = f"""
        [DATA NUTRISI PENGGUNA HARI INI]
        - Target Kalori Harian (BMR): {nutrition['target_calories']} kkal
        - Kalori Terkonsumsi: {nutrition['total_cal']} kkal
        - Protein: {nutrition['total_protein']} g
        - Karbohidrat: {nutrition['total_carbs']} g
        - Lemak: {nutrition['total_fat']} g
        Jika pengguna bertanya soal "analisis nutrisi hari ini" atau konsumsi mereka, JAWAB BERDASARKAN DATA INI.
        Beritahu mereka apa yang kurang atau berlebih.
        """

        system_prompt = _SYSTEM_PROMPT_TEMPLATE.format(nutrition_context=nutrition_context)
        full_prompt = f"{system_prompt}\n\nPesan pengguna: {message}\n\nJawaban Anda:"

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
            ai_reply = cls._call_openrouter(system_prompt, message, openrouter_key)
            if not ai_reply:
                raise RuntimeError(f"{fallback_error} | OpenRouter juga gagal merespons.")

        # Check if consultation is needed
        needs_consultation = any(t in message.lower() for t in _CONSULTATION_TRIGGERS)

        return {"reply": ai_reply, "needs_consultation": needs_consultation}

    @classmethod
    def _build_nutrition_context(cls, user_id) -> dict:
        """Gather user profile and today's nutrition data."""
        target_calories = 2000

        profile = UserModel.find_by_id(user_id)
        if profile:
            w = float(profile.get("berat_badan") or 0)
            h = float(profile.get("tinggi_badan") or 0)
            a = float(profile.get("umur") or 0)
            if w and h and a:
                gender = profile.get("jenis_kelamin", "male")
                bmr = (10 * w + 6.25 * h - 5 * a + 5) if gender == "male" else (10 * w + 6.25 * h - 5 * a - 161)
                factors = {
                    "sedentary": 1.2,
                    "light": 1.375,
                    "moderate": 1.55,
                    "active": 1.725,
                    "veryActive": 1.9,
                }
                tdee = bmr * factors.get(profile.get("aktivitas_harian", "moderate"), 1.55)
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

        food_rows = FoodAnalysisModel.find_by_user(
            user_id,
            order="tanggal.desc",
            extra_params={"tanggal": f"gte.{yesterday_utc}"},
        )

        total_cal = 0
        total_protein = 0
        total_carbs = 0
        total_fat = 0
        for f in food_rows:
            t = f.get("tanggal", "")
            clean_str = t.split("+")[0].replace("Z", "")
            if clean_str:
                dt_local = datetime.fromisoformat(clean_str) + timedelta(hours=7)
                if dt_local.strftime("%Y-%m-%d") == today_wib:
                    total_cal += float(f.get("kalori") or 0)
                    total_protein += float(f.get("protein") or 0)
                    total_carbs += float(f.get("karbohidrat") or 0)
                    total_fat += float(f.get("lemak") or 0)

        return {
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
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel("gemini-2.5-flash")
            response = model.generate_content(full_prompt)
            return response.text.strip()
        except Exception:
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
        except Exception:
            return None
