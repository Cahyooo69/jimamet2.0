"""
Business logic for chat konsultasi (live chat between user & ahli gizi).
"""

from api.models import ConsultationMessageModel, ConsultationModel


class CoachChatService:
    """Chat consultation business logic."""

    @classmethod
    def list_chat(cls, consultation_id) -> list:
        """List all chat messages for a consultation session."""
        return ConsultationMessageModel.find_by_consultation(consultation_id)

    @classmethod
    def send_chat(cls, consultation_id, sender: str, message: str) -> dict:
        """
        Send a chat message.

        Raises ValueError on validation failure.
        """
        message = message.strip()
        if not message:
            raise ValueError("Message cannot be empty.")
        if sender not in ("user", "nutritionist"):
            raise ValueError("Sender must be user or nutritionist.")

        # Verify consultation exists
        k = ConsultationModel.find_by_id(consultation_id)
        if not k:
            raise ValueError("Consultation not found.")

        return ConsultationMessageModel.create(
            {
                "consultation_id": consultation_id,
                "sender": sender,
                "message": message,
            }
        )

    @classmethod
    def delete_chat(cls, message_id) -> bool:
        """Delete a chat message."""
        return ConsultationMessageModel.delete(message_id)
