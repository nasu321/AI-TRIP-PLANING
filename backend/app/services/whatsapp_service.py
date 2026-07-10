"""
WhatsApp Delivery Service via Twilio API.
Sends travel report and PDF attachment to user's WhatsApp number.
"""
import logging
from typing import Optional
from app.config import settings

logger = logging.getLogger(__name__)


async def send_whatsapp_report(
    to_number: str,
    trip_destination: str,
    travel_score: float,
    pdf_path: Optional[str] = None,
    custom_message: Optional[str] = None,
) -> dict:
    """
    Send travel report via WhatsApp.
    Uses Twilio API or returns mock success if not configured.
    """
    if settings.USE_MOCK_WHATSAPP:
        return _mock_whatsapp_response(to_number, trip_destination)

    if not all([settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN]):
        logger.warning("Twilio credentials not configured.")
        return {"success": False, "error": "WhatsApp service not configured"}

    return await _send_via_twilio(to_number, trip_destination, travel_score, pdf_path, custom_message)


async def _send_via_twilio(
    to_number: str,
    destination: str,
    score: float,
    pdf_path: Optional[str] = None,
    custom_message: Optional[str] = None,
) -> dict:
    try:
        from twilio.rest import Client
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

        message_body = custom_message or (
            f"🌍 Your AI Travel Report for *{destination}* is ready!\n\n"
            f"✨ Travel Score: *{score:.0f}/100*\n"
            f"📋 Your personalized itinerary, hotel recommendations, flight options, and budget breakdown have been prepared.\n\n"
            f"Safe travels! ✈️\n\n"
            f"— {settings.PDF_COMPANY_NAME}"
        )

        msg_kwargs = {
            "from_": settings.TWILIO_WHATSAPP_FROM,
            "body": message_body,
            "to": f"whatsapp:{to_number}",
        }

        # If PDF path provided, add media URL (requires publicly accessible URL)
        # In production, upload to cloud storage first and pass the URL
        # msg_kwargs["media_url"] = [pdf_public_url]

        message = client.messages.create(**msg_kwargs)
        logger.info(f"WhatsApp sent to {to_number}: SID={message.sid}")

        return {
            "success": True,
            "message_sid": message.sid,
            "status": message.status,
            "to": to_number,
        }
    except Exception as e:
        logger.error(f"WhatsApp send failed: {e}")
        return {"success": False, "error": str(e)}


def _mock_whatsapp_response(to_number: str, destination: str) -> dict:
    """Return a simulated success response."""
    logger.info(f"[MOCK] WhatsApp message simulated to {to_number} for {destination}")
    return {
        "success": True,
        "message_sid": "MOCK_SID_1234567890",
        "status": "sent",
        "to": to_number,
        "note": "This is a simulated response. Configure Twilio credentials to send real messages.",
    }
