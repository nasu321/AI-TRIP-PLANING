"""
Reports router — handles PDF generation and WhatsApp delivery.
"""
import os
import logging
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models.trip import Trip
from app.models.report import Report
from app.schemas import (
    ReportGenerateRequest, ReportResponse,
    WhatsAppSendRequest, SuccessResponse, TripPlanResult
)
from app.services.pdf_service import generate_pdf_report
from app.services.whatsapp_service import send_whatsapp_report

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/reports", tags=["Reports"])


@router.post("/generate", response_model=ReportResponse)
async def generate_report(
    request: ReportGenerateRequest,
    db: AsyncSession = Depends(get_db),
):
    """Generate a PDF report for a completed trip."""
    # Load trip
    result = await db.execute(select(Trip).where(Trip.id == request.trip_id))
    trip = result.scalar_one_or_none()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    if not trip.full_result:
        raise HTTPException(status_code=400, detail="Trip must be completed before generating a report")

    try:
        trip_result = TripPlanResult(**trip.full_result)
        pdf_path = generate_pdf_report(trip_result)
        pdf_filename = os.path.basename(pdf_path)
        pdf_size = os.path.getsize(pdf_path)

        # Save report record
        report = Report(
            trip_id=trip.id,
            pdf_filename=pdf_filename,
            pdf_path=pdf_path,
            pdf_size_bytes=pdf_size,
        )
        db.add(report)
        await db.commit()
        await db.refresh(report)

        return ReportResponse(
            report_id=report.id,
            trip_id=trip.id,
            pdf_filename=pdf_filename,
            pdf_path=pdf_path,
            download_url=f"/api/reports/download/{report.id}",
            created_at=report.created_at.isoformat(),
        )
    except Exception as e:
        logger.error(f"PDF generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Report generation failed: {str(e)}")


@router.get("/download/{report_id}")
async def download_report(report_id: int, db: AsyncSession = Depends(get_db)):
    """Download a generated PDF report."""
    result = await db.execute(select(Report).where(Report.id == report_id))
    report = result.scalar_one_or_none()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    if not os.path.exists(report.pdf_path):
        raise HTTPException(status_code=404, detail="PDF file not found on disk")

    return FileResponse(
        path=report.pdf_path,
        media_type="application/pdf",
        filename=report.pdf_filename,
    )


@router.post("/send-whatsapp", response_model=SuccessResponse)
async def send_report_whatsapp(
    request: WhatsAppSendRequest,
    db: AsyncSession = Depends(get_db),
):
    """Send the travel report via WhatsApp."""
    # Load trip
    result = await db.execute(select(Trip).where(Trip.id == request.trip_id))
    trip = result.scalar_one_or_none()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")

    # Find most recent report
    report_result = await db.execute(
        select(Report).where(Report.trip_id == request.trip_id).order_by(Report.created_at.desc())
    )
    report = report_result.scalar_one_or_none()

    wa_result = await send_whatsapp_report(
        to_number=request.phone_number,
        trip_destination=trip.destination,
        travel_score=trip.travel_score or 0,
        pdf_path=report.pdf_path if report else None,
        custom_message=request.custom_message,
    )

    if wa_result.get("success"):
        if report:
            report.whatsapp_sent = True
            report.whatsapp_to = request.phone_number
            report.whatsapp_message_sid = wa_result.get("message_sid")
            report.whatsapp_sent_at = datetime.utcnow()
            await db.commit()

        return SuccessResponse(
            message=f"WhatsApp message sent to {request.phone_number}",
            data=wa_result,
        )
    else:
        raise HTTPException(
            status_code=500,
            detail=wa_result.get("error", "WhatsApp delivery failed")
        )
