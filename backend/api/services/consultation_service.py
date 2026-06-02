"""
Business logic for consultations (referral) management.
"""

from api.models import ConsultationModel, UserModel


class ConsultationService:
    """Consultations management business logic."""

    @classmethod
    def create_consultation(cls, user_id, coach_message: str) -> dict:
        """
        Create a new consultation request.

        Raises ValueError if coach_message is empty.
        """
        if not coach_message:
            raise ValueError("coach_message is required.")

        return ConsultationModel.create(
            {
                "user_id": user_id,
                "coach_message": coach_message,
                "status": "pending",
                "nutritionist_notes": "",
            }
        )

    @classmethod
    def list_consultations(cls) -> list:
        """List all consultations with patient info."""
        rows = ConsultationModel.find_all()
        result = []
        for r in rows:
            user_row = UserModel.find_by_id(r["user_id"])
            user_info = user_row if user_row else {}
            result.append(
                {
                    "id": r.get("id"),
                    "user_id": r.get("user_id"),
                    "full_name": user_info.get("full_name", "Unknown"),
                    "email": user_info.get("email", ""),
                    "coach_message": r.get("coach_message"),
                    "status": r.get("status"),
                    "nutritionist_notes": r.get("nutritionist_notes", ""),
                    "handled_by": r.get("handled_by", ""),
                    "created_at": r.get("created_at"),
                }
            )
        return result

    @classmethod
    def update_consultation(cls, consultation_id, data: dict) -> dict:
        """
        Update consultation status and/or notes.

        Raises ValueError if no valid fields provided.
        """
        update_data = {}
        if "status" in data:
            update_data["status"] = data["status"]
        if "nutritionist_notes" in data:
            update_data["nutritionist_notes"] = data["nutritionist_notes"]
        if "handled_by" in data:
            update_data["handled_by"] = data["handled_by"]
        if not update_data:
            raise ValueError("No fields to update.")

        return ConsultationModel.update(consultation_id, update_data)

    @classmethod
    def delete_consultation(cls, consultation_id) -> bool:
        """Delete a consultation record."""
        return ConsultationModel.delete(consultation_id)

    @classmethod
    def get_patient_details(cls, consultation_id: str) -> dict:
        """Get patient profile and recent food history for a consultation."""
        from api.supabase_client import supabase

        consultation = ConsultationModel.find_by_id(consultation_id)
        if not consultation:
            raise ValueError("Consultation not found.")

        user_id = consultation["user_id"]

        # Get user profile
        user_row = UserModel.find_by_id(user_id) or {}
        user_row.pop("password", None)

        # Get recent food records (last 50, newest first)
        try:
            food_history = supabase.select("food_records", {
                "user_id": f"eq.{user_id}",
                "order": "recorded_at.desc",
                "limit": "50",
            })
        except Exception:
            food_history = []

        return {
            "consultation": {
                **consultation,
                "handled_by": consultation.get("handled_by", "")
            },
            "profile": user_row,
            "food_history": food_history,
        }
