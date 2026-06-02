"""
Business logic for food analysis and dashboard.
Dashboard summary is cached for 60 seconds per user+date.
"""

from datetime import date, datetime, timedelta

from api.models import FoodRecordModel, UserModel
from api import cache as app_cache


class AnalysisService:
    """Food analysis and dashboard business logic with caching."""

    @classmethod
    def list_food_records(cls, user_id, date_from: str = None, date_to: str = None) -> list:
        """List food records for a user with optional date filters."""
        # Only cache the unfiltered listing
        if not date_from and not date_to:
            cache_key = app_cache.key_food_records(user_id)
            cached = app_cache.get(cache_key)
            if cached is not None:
                return cached

        extra_params = {}
        if date_from:
            extra_params["recorded_at"] = f"gte.{date_from}"
        if date_to:
            extra_params["recorded_at"] = f"lte.{date_to}"

        result = FoodRecordModel.find_by_user(user_id, extra_params=extra_params)

        if not date_from and not date_to:
            app_cache.set(app_cache.key_food_records(user_id), result, app_cache.TTL_FOOD_RECORDS)

        return result

    @classmethod
    def create_food_record(cls, user_id, data: dict) -> dict:
        """
        Create a new food consumption record.
        Invalidates dashboard and food record caches.
        Raises ValueError if required fields are missing.
        """
        food_name = data.get("food_name") or data.get("nama_makanan")
        calories = data.get("calories") or data.get("kalori")
        if not food_name:
            raise ValueError("food_name / nama_makanan is required.")
        if calories is None:
            raise ValueError("calories / kalori is required.")

        record = {
            "user_id": user_id,
            "food_name": data.get("food_name") or data.get("nama_makanan"),
            "calories": data.get("calories") or data.get("kalori", 0),
            "protein": data.get("protein", 0),
            "fat": data.get("fat") or data.get("lemak", 0),
            "carbs": data.get("carbs") or data.get("karbohidrat", 0),
            "sugar": data.get("sugar") or data.get("gula", 0),
            "recorded_at": data.get("recorded_at") or data.get("tanggal") or datetime.utcnow().isoformat() + "Z",
        }

        result = FoodRecordModel.create(record)

        # Invalidate caches
        app_cache.delete(app_cache.key_food_records(user_id))
        # Dashboard keys include date — invalidate today's
        today = (datetime.utcnow() + timedelta(hours=7)).strftime("%Y-%m-%d")
        app_cache.delete(app_cache.key_dashboard(user_id, today))

        return result

    @classmethod
    def get_food_record(cls, user_id, record_id) -> dict:
        """Get a single food record. Raises ValueError if not found."""
        row = FoodRecordModel.find_by_id_and_user(record_id, user_id)
        if not row:
            raise ValueError("Record not found.")
        return row

    @classmethod
    def delete_food_record(cls, user_id, record_id) -> bool:
        """Delete a food record. Invalidates caches."""
        result = FoodRecordModel.delete(record_id, user_id)

        app_cache.delete(app_cache.key_food_records(user_id))
        today = (datetime.utcnow() + timedelta(hours=7)).strftime("%Y-%m-%d")
        app_cache.delete(app_cache.key_dashboard(user_id, today))

        return result

    @classmethod
    def get_dashboard_summary(cls, user_id, target_date: str) -> dict:
        """
        Calculate daily nutrition summary and 7-day trend.
        Cached for 60 seconds per user+date.
        """
        cache_key = app_cache.key_dashboard(user_id, target_date)
        cached = app_cache.get(cache_key)
        if cached is not None:
            return cached

        d = date.fromisoformat(target_date)
        seven_days_ago = (d - timedelta(days=6)).isoformat()

        food_rows = FoodRecordModel.find_by_user(
            user_id,
            order="recorded_at.desc",
            extra_params={"recorded_at": f"gte.{seven_days_ago}T00:00:00"},
        )

        today_rows = [r for r in food_rows if cls._get_local_date_str(r.get("recorded_at", "")) == target_date]

        weekly_cals = {(d - timedelta(days=i)).isoformat(): 0 for i in range(7)}
        for r in food_rows:
            date_str = cls._get_local_date_str(r.get("recorded_at", ""))
            if date_str in weekly_cals:
                weekly_cals[date_str] += float(r.get("calories") or 0)

        weekly_data = []
        for i in range(6, -1, -1):
            dt = (d - timedelta(days=i)).isoformat()
            weekly_data.append({"date": dt, "calories": weekly_cals[dt]})

        total_cal = sum(float(r.get("calories", 0) or 0) for r in today_rows)
        total_protein = sum(float(r.get("protein", 0) or 0) for r in today_rows)
        total_fat = sum(float(r.get("fat", 0) or 0) for r in today_rows)
        total_carbs = sum(float(r.get("carbs", 0) or 0) for r in today_rows)

        # Ambil target kalori dari profil user
        user_profile = UserModel.find_by_id(user_id)
        target_calories = user_profile.get("daily_calorie_target") if user_profile else 2000
        
        result = {
            "date": target_date,
            "total_meals": len(today_rows),
            "total_calories": total_cal,
            "target_calories": target_calories,
            "total_protein": total_protein,
            "total_carbs": total_carbs,
            "total_fat": total_fat,
            "total_fiber": 0,
            "meals": today_rows,
            "weekly_data": weekly_data,
        }

        app_cache.set(cache_key, result, app_cache.TTL_DASHBOARD)
        return result

    @staticmethod
    def _get_local_date_str(iso_str: str) -> str:
        """Convert UTC ISO string to WIB (UTC+7) date string YYYY-MM-DD."""
        if not iso_str:
            return ""
        try:
            clean_str = iso_str.split("+")[0].replace("Z", "")
            dt = datetime.fromisoformat(clean_str)
            dt_local = dt + timedelta(hours=7)
            return dt_local.strftime("%Y-%m-%d")
        except Exception:
            return iso_str[:10]
