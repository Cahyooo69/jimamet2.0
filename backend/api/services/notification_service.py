"""
Business logic for konsultasi (notification/referral) management.
"""

from api.models import NotificationModel, UserModel


class NotificationService:
    """Konsultasi management business logic."""

    @classmethod
    def create_konsultasi(cls, user_id, pesan_coachbot: str) -> dict:
        """
        Create a new konsultasi request.

        Raises ValueError if pesan_coachbot is empty.
        """
        if not pesan_coachbot:
            raise ValueError("pesan_coachbot is required.")

        return NotificationModel.create(
            {
                "id_user": user_id,
                "pesan_coachbot": pesan_coachbot,
                "status": "menunggu",
                "catatan_ahli_gizi": "",
            }
        )

    @classmethod
    def list_konsultasi(cls) -> list:
        """List all konsultasi with patient info."""
        rows = NotificationModel.find_all()
        result = []
        for r in rows:
            user_row = UserModel.find_by_id(r["id_user"])
            user_info = user_row if user_row else {}
            result.append(
                {
                    "id_konsultasi": r.get("id_konsultasi"),
                    "id_user": r.get("id_user"),
                    "nama_pasien": user_info.get("nama", "Unknown"),
                    "email_pasien": user_info.get("email", ""),
                    "pesan_coachbot": r.get("pesan_coachbot"),
                    "status": r.get("status"),
                    "catatan_ahli_gizi": r.get("catatan_ahli_gizi", ""),
                    "tanggal": r.get("tanggal"),
                }
            )
        return result

    @classmethod
    def update_konsultasi(cls, konsultasi_id, data: dict) -> dict:
        """
        Update konsultasi status and/or notes.

        Raises ValueError if no valid fields provided.
        """
        update_data = {}
        if "status" in data:
            update_data["status"] = data["status"]
        if "catatan_ahli_gizi" in data:
            update_data["catatan_ahli_gizi"] = data["catatan_ahli_gizi"]
        if not update_data:
            raise ValueError("No fields to update.")

        return NotificationModel.update(konsultasi_id, update_data)

    @classmethod
    def delete_konsultasi(cls, konsultasi_id) -> bool:
        """Delete a konsultasi record."""
        return NotificationModel.delete(konsultasi_id)
