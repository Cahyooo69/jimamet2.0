"""
Business logic for food analysis and dashboard.
"""

from datetime import date, datetime, timedelta

from api.models import FoodAnalysisModel


class AnalysisService:
    """Food analysis and dashboard business logic."""

    @classmethod
    def list_food_records(cls, user_id, date_from: str = None, date_to: str = None) -> list:
        """List food records for a user with optional date filters."""
        extra_params = {}
        if date_from:
            extra_params["tanggal"] = f"gte.{date_from}"
        if date_to:
            extra_params["tanggal"] = f"lte.{date_to}"
        return FoodAnalysisModel.find_by_user(user_id, extra_params=extra_params)

    @classmethod
    def create_food_record(cls, user_id, data: dict) -> dict:
        """
        Create a new food consumption record.

        Raises ValueError if required fields are missing.
        """
        required = ["nama_makanan", "kalori"]
        for field in required:
            if field not in data:
                raise ValueError(f"{field} is required.")

        record = {
            "id_user": user_id,
            "nama_makanan": data.get("nama_makanan") or data.get("food_name"),
            "kalori": data.get("kalori") or data.get("calories", 0),
            "protein": data.get("protein", 0),
            "lemak": data.get("lemak") or data.get("fat", 0),
            "karbohidrat": data.get("karbohidrat") or data.get("carbs", 0),
            "gula": data.get("gula") or data.get("sugar", 0),
            "tanggal": data.get("tanggal") or datetime.utcnow().isoformat() + "Z",
        }

        return FoodAnalysisModel.create(record)

    @classmethod
    def get_food_record(cls, user_id, record_id) -> dict:
        """
        Get a single food record.

        Raises ValueError if not found.
        """
        row = FoodAnalysisModel.find_by_id_and_user(record_id, user_id)
        if not row:
            raise ValueError("Record not found.")
        return row

    @classmethod
    def delete_food_record(cls, user_id, record_id) -> bool:
        """Delete a food record."""
        return FoodAnalysisModel.delete(record_id, user_id)

    @classmethod
    def get_dashboard_summary(cls, user_id, target_date: str) -> dict:
        """
        Calculate daily nutrition summary and 7-day trend.

        Args:
            user_id: The user's ID.
            target_date: ISO format date string (YYYY-MM-DD).

        Returns:
            Dict with totals, meals list, and weekly_data.
        """
        d = date.fromisoformat(target_date)
        seven_days_ago = (d - timedelta(days=6)).isoformat()

        # Fetch food records for the last 7 days
        food_rows = FoodAnalysisModel.find_by_user(
            user_id,
            order="tanggal.desc",
            extra_params={"tanggal": f"gte.{seven_days_ago}T00:00:00"},
        )

        # Filter today's rows based on WIB timezone
        today_rows = [r for r in food_rows if cls._get_local_date_str(r.get("tanggal", "")) == target_date]

        # Build weekly calorie data
        weekly_cals = {(d - timedelta(days=i)).isoformat(): 0 for i in range(7)}
        for r in food_rows:
            date_str = cls._get_local_date_str(r.get("tanggal", ""))
            if date_str in weekly_cals:
                weekly_cals[date_str] += float(r.get("kalori") or 0)

        weekly_data = []
        for i in range(6, -1, -1):
            dt = (d - timedelta(days=i)).isoformat()
            weekly_data.append({"date": dt, "calories": weekly_cals[dt]})

        # Calculate daily totals
        total_cal = sum(float(r.get("kalori", 0) or 0) for r in today_rows)
        total_protein = sum(float(r.get("protein", 0) or 0) for r in today_rows)
        total_fat = sum(float(r.get("lemak", 0) or 0) for r in today_rows)
        total_carbs = sum(float(r.get("karbohidrat", 0) or 0) for r in today_rows)

        return {
            "date": target_date,
            "total_meals": len(today_rows),
            "total_calories": total_cal,
            "total_protein": total_protein,
            "total_carbs": total_carbs,
            "total_fat": total_fat,
            "total_fiber": 0,
            "meals": today_rows,
            "weekly_data": weekly_data,
        }

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
