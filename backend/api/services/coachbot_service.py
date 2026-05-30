"""
Business logic for chat konsultasi (live chat between user & ahli gizi).
"""

from api.models import ChatKonsultasiModel, NotificationModel


class CoachbotService:
    """Chat konsultasi business logic."""

    @classmethod
    def list_chat(cls, konsultasi_id) -> list:
        """List all chat messages for a konsultasi session."""
        return ChatKonsultasiModel.find_by_konsultasi(konsultasi_id)

    @classmethod
    def send_chat(cls, konsultasi_id, pengirim: str, pesan: str) -> dict:
        """
        Send a chat message.

        Raises ValueError on validation failure.
        """
        pesan = pesan.strip()
        if not pesan:
            raise ValueError("pesan tidak boleh kosong.")
        if pengirim not in ("user", "ahli_gizi"):
            raise ValueError("pengirim harus user atau ahli_gizi.")

        # Verify konsultasi exists
        k = NotificationModel.find_by_id(konsultasi_id)
        if not k:
            raise ValueError("Konsultasi tidak ditemukan.")

        return ChatKonsultasiModel.create(
            {
                "id_konsultasi": konsultasi_id,
                "pengirim": pengirim,
                "pesan": pesan,
            }
        )

    @classmethod
    def delete_chat(cls, chat_id) -> bool:
        """Delete a chat message."""
        return ChatKonsultasiModel.delete(chat_id)
