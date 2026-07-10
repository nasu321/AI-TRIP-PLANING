"""
PDF Report Generation Service using ReportLab.
Produces a professional, visually formatted travel report PDF.
"""
import os
import io
import logging
from datetime import datetime
from typing import Optional
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, mm
from reportlab.lib.utils import ImageReader
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak, KeepTogether
)
from reportlab.graphics.shapes import Drawing, Rect, String
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics import renderPDF
from reportlab.pdfgen import canvas

from app.schemas import TripPlanResult
from app.config import settings

logger = logging.getLogger(__name__)

# Brand Colors
PRIMARY = colors.HexColor("#1a1a2e")       # Deep navy
ACCENT = colors.HexColor("#e94560")        # Vibrant red/pink
SECONDARY = colors.HexColor("#16213e")     # Dark blue
GOLD = colors.HexColor("#f5a623")          # Gold accent
LIGHT_BG = colors.HexColor("#f8f9ff")      # Light background
TEXT_DARK = colors.HexColor("#1a1a2e")
TEXT_LIGHT = colors.white
TEXT_MUTED = colors.HexColor("#666680")
SUCCESS = colors.HexColor("#00b894")       # Green
WARNING = colors.HexColor("#fdcb6e")       # Yellow


def ensure_reports_dir() -> Path:
    reports_dir = Path(settings.REPORTS_DIR)
    reports_dir.mkdir(parents=True, exist_ok=True)
    return reports_dir


def score_color(score: float) -> colors.Color:
    if score >= 80:
        return SUCCESS
    elif score >= 60:
        return GOLD
    else:
        return ACCENT


def generate_pdf_report(trip_result: TripPlanResult) -> str:
    """
    Generate a full PDF travel report and return the file path.
    """
    reports_dir = ensure_reports_dir()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"travel_report_{trip_result.destination.replace(' ', '_')}_{timestamp}.pdf"
    filepath = reports_dir / filename

    doc = SimpleDocTemplate(
        str(filepath),
        pagesize=A4,
        rightMargin=20*mm,
        leftMargin=20*mm,
        topMargin=25*mm,
        bottomMargin=20*mm,
        title=f"Travel Report: {trip_result.destination}",
        author=settings.PDF_COMPANY_NAME,
    )

    styles = _build_styles()
    story = []

    # ── Cover Header ─────────────────────────────
    story.extend(_build_cover(trip_result, styles))
    story.append(PageBreak())

    # ── Travel Score Section ──────────────────────
    story.extend(_build_travel_score_section(trip_result, styles))
    story.append(Spacer(1, 15))

    # ── Weather Section ───────────────────────────
    story.extend(_build_weather_section(trip_result, styles))
    story.append(Spacer(1, 15))

    # ── Tourist Places ────────────────────────────
    story.extend(_build_attractions_section(trip_result, styles))
    story.append(PageBreak())

    # ── Recommended Hotels ────────────────────────
    story.extend(_build_hotels_section(trip_result, styles))
    story.append(Spacer(1, 15))

    # ── Flight Options ────────────────────────────
    story.extend(_build_flights_section(trip_result, styles))
    story.append(Spacer(1, 15))

    # ── Budget Breakdown ──────────────────────────
    story.extend(_build_budget_section(trip_result, styles))
    story.append(PageBreak())

    # ── Daily Itinerary + Weather ─────────────────
    story.extend(_build_itinerary_section(trip_result, styles))
    story.append(Spacer(1, 15))

    # ── Review Insights ───────────────────────────
    story.extend(_build_reviews_section(trip_result, styles))
    story.append(Spacer(1, 15))

    # ── Personalized Tips ─────────────────────────
    story.extend(_build_tips_section(trip_result, styles))

    # Build PDF
    doc.build(story, onFirstPage=_header_footer, onLaterPages=_header_footer)
    logger.info(f"✅ PDF report generated: {filepath}")
    return str(filepath)


def _build_styles():
    styles = getSampleStyleSheet()
    custom = {
        "Title": ParagraphStyle("Title", fontSize=28, textColor=TEXT_LIGHT,
                                fontName="Helvetica-Bold", spaceAfter=6, alignment=1),
        "Subtitle": ParagraphStyle("Subtitle", fontSize=14, textColor=TEXT_LIGHT,
                                   fontName="Helvetica", spaceAfter=4, alignment=1),
        "SectionTitle": ParagraphStyle("SectionTitle", fontSize=16, textColor=PRIMARY,
                                        fontName="Helvetica-Bold", spaceBefore=10, spaceAfter=8),
        "Body": ParagraphStyle("Body", fontSize=10, textColor=TEXT_DARK,
                                fontName="Helvetica", spaceAfter=4, leading=14),
        "BoldBody": ParagraphStyle("BoldBody", fontSize=10, textColor=TEXT_DARK,
                                    fontName="Helvetica-Bold", spaceAfter=4),
        "Muted": ParagraphStyle("Muted", fontSize=9, textColor=TEXT_MUTED,
                                 fontName="Helvetica", spaceAfter=3),
        "SmallBold": ParagraphStyle("SmallBold", fontSize=9, textColor=TEXT_DARK,
                                     fontName="Helvetica-Bold"),
        "AgentNote": ParagraphStyle("AgentNote", fontSize=9, textColor=TEXT_MUTED,
                                     fontName="Helvetica-Oblique", spaceAfter=4, leading=13),
    }
    return custom


def _header_footer(canvas_obj, doc):
    """Draw consistent header/footer on every page."""
    canvas_obj.saveState()
    w, h = A4

    # Footer
    canvas_obj.setFillColor(PRIMARY)
    canvas_obj.rect(0, 0, w, 20*mm, fill=True, stroke=False)
    canvas_obj.setFillColor(TEXT_LIGHT)
    canvas_obj.setFont("Helvetica", 8)
    canvas_obj.drawString(20*mm, 7*mm, f"© {datetime.now().year} {settings.PDF_COMPANY_NAME}  |  {settings.PDF_SUPPORT_EMAIL}")
    canvas_obj.drawRightString(w - 20*mm, 7*mm, f"Page {doc.page}")

    # Header bar (on later pages)
    if doc.page > 1:
        canvas_obj.setFillColor(PRIMARY)
        canvas_obj.rect(0, h - 15*mm, w, 15*mm, fill=True, stroke=False)
        canvas_obj.setFillColor(ACCENT)
        canvas_obj.rect(0, h - 15*mm, 4*mm, 15*mm, fill=True, stroke=False)
        canvas_obj.setFillColor(TEXT_LIGHT)
        canvas_obj.setFont("Helvetica-Bold", 9)
        canvas_obj.drawString(10*mm, h - 8*mm, "🌍 AI Travel Platform — Confidential Travel Report")

    canvas_obj.restoreState()


def _build_cover(result: TripPlanResult, styles) -> list:
    items = []
    # Cover table with gradient background effect
    cover_data = [
        [Paragraph(f"🌍 {result.destination}", styles["Title"])],
        [Paragraph("AI-Powered Travel Report", styles["Subtitle"])],
        [Paragraph(f"Travel Score: {result.travel_score.total:.0f}/100 — {result.travel_score.label}", styles["Subtitle"])],
        [Paragraph(f"Generated: {datetime.now().strftime('%B %d, %Y')}", styles["Subtitle"])],
    ]
    cover_table = Table(cover_data, colWidths=[170*mm])
    cover_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), PRIMARY),
        ("TOPPADDING", (0, 0), (-1, -1), 18),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 18),
        ("LEFTPADDING", (0, 0), (-1, -1), 20),
        ("RIGHTPADDING", (0, 0), (-1, -1), 20),
        ("ROWBACKGROUNDS", (0, 0), (-1, 0), [PRIMARY]),
    ]))
    items.append(cover_table)
    items.append(Spacer(1, 20))

    # AI Reasoning Summary
    items.append(Paragraph("✨ AI Agent Summary", styles["SectionTitle"]))
    items.append(HRFlowable(width="100%", thickness=1, color=ACCENT, spaceAfter=8))
    items.append(Paragraph(result.agent_reasoning, styles["AgentNote"]))
    return items


def _build_travel_score_section(result: TripPlanResult, styles) -> list:
    items = []
    items.append(Paragraph("📊 Travel Score Breakdown", styles["SectionTitle"]))
    items.append(HRFlowable(width="100%", thickness=1, color=ACCENT, spaceAfter=8))

    score = result.travel_score
    score_data = [
        ["Metric", "Score", "Rating"],
        ["🌤️ Weather", f"{score.weather_score:.0f}/100", _score_badge(score.weather_score)],
        ["💰 Budget Fit", f"{score.budget_score:.0f}/100", _score_badge(score.budget_score)],
        ["🏨 Hotel Quality", f"{score.hotel_score:.0f}/100", _score_badge(score.hotel_score)],
        ["💬 Sentiment", f"{score.sentiment_score:.0f}/100", _score_badge(score.sentiment_score)],
        ["✈️ Flight Affordability", f"{score.flight_score:.0f}/100", _score_badge(score.flight_score)],
        ["⭐ OVERALL SCORE", f"{score.total:.0f}/100", score.label.upper()],
    ]

    score_table = Table(score_data, colWidths=[80*mm, 50*mm, 40*mm])
    score_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), PRIMARY),
        ("TEXTCOLOR", (0, 0), (-1, 0), TEXT_LIGHT),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 10),
        ("FONTNAME", (0, 1), (-1, -2), "Helvetica"),
        ("FONTSIZE", (0, 1), (-1, -1), 10),
        ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, -1), (-1, -1), 11),
        ("BACKGROUND", (0, -1), (-1, -1), ACCENT),
        ("TEXTCOLOR", (0, -1), (-1, -1), TEXT_LIGHT),
        ("ROWBACKGROUNDS", (0, 1), (-1, -2), [LIGHT_BG, colors.white]),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#dde1f0")),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LEFTPADDING", (0, 0), (-1, -1), 12),
        ("ALIGN", (1, 0), (2, -1), "CENTER"),
    ]))
    items.append(score_table)
    items.append(Spacer(1, 8))
    items.append(Paragraph(f"💡 {score.explanation}", styles["Muted"]))
    return items


def _build_weather_section(result: TripPlanResult, styles) -> list:
    items = []
    items.append(Paragraph("🌤️ Weather Forecast & Suitability", styles["SectionTitle"]))
    items.append(HRFlowable(width="100%", thickness=1, color=ACCENT, spaceAfter=8))

    weather = result.weather
    items.append(Paragraph(
        f"Suitability: <b>{weather.suitability_label}</b> ({weather.suitability_score:.0f}/100) — {weather.best_time_note}",
        styles["Body"]
    ))
    items.append(Spacer(1, 6))

    # Forecast table
    weather_data = [["Day", "Condition", "High", "Low", "Humidity", "Precip"]]
    for day in weather.forecast:
        weather_data.append([
            day.date, f"{day.icon} {day.condition}",
            f"{day.temp_high_c}°C", f"{day.temp_low_c}°C",
            f"{day.humidity_pct}%", f"{day.precipitation_mm}mm"
        ])

    w_table = Table(weather_data, colWidths=[20*mm, 55*mm, 22*mm, 22*mm, 24*mm, 22*mm])
    w_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), PRIMARY),
        ("TEXTCOLOR", (0, 0), (-1, 0), TEXT_LIGHT),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [LIGHT_BG, colors.white]),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#dde1f0")),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("ALIGN", (2, 0), (-1, -1), "CENTER"),
    ]))
    items.append(w_table)

    # Packing tips
    items.append(Spacer(1, 8))
    items.append(Paragraph("🎒 Packing Tips:", styles["BoldBody"]))
    for tip in weather.packing_tips[:4]:
        items.append(Paragraph(f"  • {tip}", styles["Body"]))
    return items


def _build_hotels_section(result: TripPlanResult, styles) -> list:
    items = []
    items.append(Paragraph("🏨 Recommended Hotels", styles["SectionTitle"]))
    items.append(HRFlowable(width="100%", thickness=1, color=ACCENT, spaceAfter=8))

    hotel_data = [["Hotel", "Price/Night", "Rating", "Rec. Score", "Sentiment"]]
    table_text_style = ParagraphStyle("TableText", fontSize=9, textColor=TEXT_DARK, fontName="Helvetica", leading=11)
    
    for hotel in result.recommended_hotels[:4]:
        badge = "⭐ TOP PICK" if hotel.is_recommended else ""
        hotel_data.append([
            Paragraph(f"{hotel.hotel_name} {badge}", table_text_style),
            f"${hotel.price_per_night_usd:.0f}",
            f"{'⭐' * int(hotel.rating)} {hotel.rating}",
            f"{hotel.recommendation_score:.0f}/100",
            f"{hotel.sentiment_score*100:.0f}% 👍",
        ])

    h_table = Table(hotel_data, colWidths=[65*mm, 25*mm, 30*mm, 25*mm, 25*mm])
    h_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), PRIMARY),
        ("TEXTCOLOR", (0, 0), (-1, 0), TEXT_LIGHT),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [LIGHT_BG, colors.white]),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#dde1f0")),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
        ("ALIGN", (1, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    items.append(h_table)
    return items


def _build_flights_section(result: TripPlanResult, styles) -> list:
    items = []
    items.append(Paragraph("✈️ Flight Options", styles["SectionTitle"]))
    items.append(HRFlowable(width="100%", thickness=1, color=ACCENT, spaceAfter=8))

    flight_data = [["Airline", "Price", "Duration", "Stops", "Departs", "Arrives"]]
    for f in result.flights:
        badge = "💸 BEST PRICE" if f.is_cheapest else ""
        flight_data.append([
            f"{f.airline} {badge}",
            f"${f.price_usd:.0f}",
            f"{f.duration_hours:.1f}h",
            str(f.stops),
            f.departure_time,
            f.arrival_time,
        ])

    f_table = Table(flight_data, colWidths=[55*mm, 25*mm, 25*mm, 20*mm, 22*mm, 22*mm])
    f_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), PRIMARY),
        ("TEXTCOLOR", (0, 0), (-1, 0), TEXT_LIGHT),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [LIGHT_BG, colors.white]),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#dde1f0")),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("ALIGN", (1, 0), (-1, -1), "CENTER"),
    ]))
    items.append(f_table)
    return items


def _build_budget_section(result: TripPlanResult, styles) -> list:
    items = []
    items.append(Paragraph("💰 Budget Breakdown", styles["SectionTitle"]))
    items.append(HRFlowable(width="100%", thickness=1, color=ACCENT, spaceAfter=8))

    budget = result.budget
    budget_data = [
        ["Category", "Estimated Cost", "% of Total"],
        ["✈️ Flights", f"${budget.flight_cost_usd:,.0f}", f"{budget.flight_cost_usd/max(budget.total_estimated_usd,1)*100:.0f}%"],
        ["🏨 Hotels", f"${budget.hotel_total_usd:,.0f}", f"{budget.hotel_total_usd/max(budget.total_estimated_usd,1)*100:.0f}%"],
        ["🎭 Activities", f"${budget.activities_total_usd:,.0f}", f"{budget.activities_total_usd/max(budget.total_estimated_usd,1)*100:.0f}%"],
        ["🍽️ Food", f"${budget.food_total_usd:,.0f}", f"{budget.food_total_usd/max(budget.total_estimated_usd,1)*100:.0f}%"],
        ["🚌 Local Transport", f"${budget.transport_local_usd:,.0f}", f"{budget.transport_local_usd/max(budget.total_estimated_usd,1)*100:.0f}%"],
        ["📦 Miscellaneous", f"${budget.misc_usd:,.0f}", f"{budget.misc_usd/max(budget.total_estimated_usd,1)*100:.0f}%"],
        ["💳 TOTAL ESTIMATED", f"${budget.total_estimated_usd:,.0f}", "100%"],
        ["💚 Budget Remaining", f"${budget.budget_remaining_usd:,.0f}", ""],
    ]

    b_table = Table(budget_data, colWidths=[80*mm, 50*mm, 40*mm])
    b_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), PRIMARY),
        ("TEXTCOLOR", (0, 0), (-1, 0), TEXT_LIGHT),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTNAME", (0, -2), (-1, -2), "Helvetica-Bold"),
        ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
        ("BACKGROUND", (0, -2), (-1, -2), ACCENT),
        ("TEXTCOLOR", (0, -2), (-1, -2), TEXT_LIGHT),
        ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#d4edda")),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("ROWBACKGROUNDS", (0, 1), (-1, -3), [LIGHT_BG, colors.white]),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#dde1f0")),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
        ("ALIGN", (1, 0), (-1, -1), "CENTER"),
    ]))
    items.append(b_table)

    items.append(Spacer(1, 8))
    items.append(Paragraph(f"Budget Fit: <b>{budget.budget_fit_label}</b> ({budget.budget_fit_score:.0f}/100)", styles["Body"]))

    if budget.cost_saving_tips:
        items.append(Paragraph("💡 Cost Saving Tips:", styles["BoldBody"]))
        for tip in budget.cost_saving_tips[:3]:
            items.append(Paragraph(f"  • {tip}", styles["Body"]))
    return items


def _build_attractions_section(result: TripPlanResult, styles) -> list:
    items = []
    items.append(Paragraph("🗺️ Tourist Places & Trip Summary", styles["SectionTitle"]))
    items.append(HRFlowable(width="100%", thickness=1, color=ACCENT, spaceAfter=8))

    # Add a short trip summary
    dest_city = result.destination.split(',')[0]
    total_cost = f"${result.budget.total_estimated_usd:,.0f}" if result.budget else "Unknown"
    summary_text = (
        f"<b>Summary:</b> A {len(result.itinerary)}-day trip to {result.destination}, "
        f"featuring {len(result.attractions)} top attractions. "
        f"The AI has planned this itinerary with an estimated total budget of {total_cost} "
        f"and an overall travel score of {result.travel_score.total:.0f}/100."
    )
    items.append(Paragraph(summary_text, styles["Body"]))
    items.append(Spacer(1, 10))

    if not result.attractions:
        items.append(Paragraph("No attraction data available for this destination.", styles["Body"]))
        return items

    attr_data = [["Attraction & City", "Category", "Rating", "Duration", "Entry Fee"]]
    table_text_style = ParagraphStyle("TableText", fontSize=9, textColor=TEXT_DARK, fontName="Helvetica", leading=11)
    
    for i, attr in enumerate(result.attractions):
        attr_data.append([
            Paragraph(f"{attr.name} ({dest_city})", table_text_style),
            attr.category,
            f"{'★' * int(attr.rating)} {attr.rating}",
            f"{attr.estimated_duration_hours:.1f}h",
            f"${attr.entry_fee_usd:.0f}" if attr.entry_fee_usd else "Free",
        ])

    a_table = Table(attr_data, colWidths=[70*mm, 30*mm, 25*mm, 25*mm, 20*mm])
    a_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), PRIMARY),
        ("TEXTCOLOR", (0, 0), (-1, 0), TEXT_LIGHT),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [LIGHT_BG, colors.white]),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#dde1f0")),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
        ("ALIGN", (2, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    items.append(a_table)

    # Descriptions
    items.append(Spacer(1, 10))
    items.append(Paragraph("Attraction Highlights:", styles["BoldBody"]))
    for attr in result.attractions[:6]:
        items.append(Paragraph(
            f"  • {attr.name} ({attr.category}): {attr.description[:100]}..."
            if len(attr.description) > 100 else f"  • {attr.name} ({attr.category}): {attr.description}",
            styles["Muted"]
        ))
    return items


def _build_itinerary_section(result: TripPlanResult, styles) -> list:
    items = []
    items.append(Paragraph("📅 Day-by-Day Itinerary with Weather & Tourist Spots", styles["SectionTitle"]))
    items.append(HRFlowable(width="100%", thickness=1, color=ACCENT, spaceAfter=8))

    weather_forecast = []
    if result.weather and result.weather.forecast:
        weather_forecast = result.weather.forecast

    # Attraction pool for day assignment
    attr_names = [a.name for a in result.attractions] if result.attractions else []

    for day in result.itinerary:
        # Day header with weather
        w_text = ""
        if weather_forecast and day.day_number <= len(weather_forecast):
            wd = weather_forecast[day.day_number - 1]
            w_text = f"  |  {wd.icon} {wd.condition} {wd.temp_high_c:.0f}C/{wd.temp_low_c:.0f}C  Rain:{wd.precipitation_mm:.0f}mm"

        # Weather impact note
        impact = ""
        if weather_forecast and day.day_number <= len(weather_forecast):
            wd = weather_forecast[day.day_number - 1]
            if wd.precipitation_mm > 10:
                impact = "WEATHER ALERT: Heavy rain — prioritise indoor venues"
            elif wd.temp_high_c > 35:
                impact = "WEATHER NOTE: Very hot — outdoor visits before 11 AM"

        # Tourist spots for this day
        spots = []
        if attr_names:
            primary_idx = (day.day_number - 1) % len(attr_names)
            spots.append(attr_names[primary_idx])
            if 1 < day.day_number < len(result.itinerary) and len(attr_names) > 1:
                sec_idx = day.day_number % len(attr_names)
                if sec_idx != primary_idx:
                    spots.append(attr_names[sec_idx])

        # Build table row data
        itin_data = []
        itin_data.append([f"DAY {day.day_number}: {day.title.upper()}{w_text}"])

        day_block_data = []
        # Parse structured activities
        morning = afternoon = evening = []
        for act in day.activities:
            if act.startswith("MORNING:"):
                morning = [a.strip() for a in act.replace("MORNING:", "").split("|") if a.strip()]
            elif act.startswith("AFTERNOON:"):
                afternoon = [a.strip() for a in act.replace("AFTERNOON:", "").split("|") if a.strip()]
            elif act.startswith("EVENING:"):
                evening = [a.strip() for a in act.replace("EVENING:", "").split("|") if a.strip()]

        rows = []
        if morning:
            rows.append(["Sunrise Morning", " | ".join(morning[:3])])
        if afternoon:
            rows.append(["Afternoon", " | ".join(afternoon[:3])])
        if evening:
            rows.append(["Evening", " | ".join(evening[:2])])
        if spots:
            rows.append(["Tourist Spots", " + ".join(spots)])
        if day.meals:
            rows.append(["Meals", " | ".join(day.meals)])
        rows.append(["Stay", f"{day.accommodation}  |  Budget: ~${day.estimated_daily_cost_usd:.0f}"])
        if impact:
            rows.append(["! Weather Alert", impact])

        d_table = Table(rows, colWidths=[38*mm, 132*mm])
        style_cmds = [
            ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
            ("FONTNAME", (1, 0), (1, -1), "Helvetica"),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("TEXTCOLOR", (0, 0), (0, -1), TEXT_MUTED),
            ("ROWBACKGROUNDS", (0, 0), (-1, -1), [LIGHT_BG, colors.white]),
            ("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#e8ecf5")),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ]
        # Highlight tourist spots row
        for ri, row in enumerate(rows):
            if row[0] == "Tourist Spots":
                style_cmds.append(("BACKGROUND", (0, ri), (-1, ri), colors.HexColor("#f0ebff")))
                style_cmds.append(("TEXTCOLOR", (1, ri), (1, ri), colors.HexColor("#7c3aed")))
            if row[0] == "! Weather Alert":
                style_cmds.append(("BACKGROUND", (0, ri), (-1, ri), colors.HexColor("#fff3cd")))
                style_cmds.append(("TEXTCOLOR", (0, ri), (-1, ri), colors.HexColor("#856404")))
        d_table.setStyle(TableStyle(style_cmds))

        # Day title bar
        header_table = Table([[Paragraph(
            f"<b>Day {day.day_number}: {day.title}</b>{(' — ' + w_text.strip()) if w_text else ''}",
            styles["SmallBold"]
        )]], colWidths=[170*mm])
        header_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), PRIMARY),
            ("TEXTCOLOR", (0, 0), (-1, -1), TEXT_LIGHT),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ]))
        items.append(KeepTogether([header_table, d_table, Spacer(1, 8)]))

    return items


def _build_reviews_section(result: TripPlanResult, styles) -> list:
    items = []
    items.append(Paragraph("💬 Review Intelligence", styles["SectionTitle"]))
    items.append(HRFlowable(width="100%", thickness=1, color=ACCENT, spaceAfter=8))

    for insight in result.review_insights[:3]:
        items.append(Paragraph(f"📍 {insight.hotel_name}", styles["BoldBody"]))
        items.append(Paragraph(
            f"  {insight.positive_pct:.0f}% positive  |  {insight.total_reviews:,} reviews",
            styles["Muted"]
        ))
        items.append(Paragraph(f"  {insight.ai_summary}", styles["AgentNote"]))
        items.append(Spacer(1, 5))
    return items


def _build_tips_section(result: TripPlanResult, styles) -> list:
    items = []
    items.append(Paragraph("✨ Personalized Travel Tips", styles["SectionTitle"]))
    items.append(HRFlowable(width="100%", thickness=1, color=ACCENT, spaceAfter=8))

    for tip in result.personalized_tips:
        items.append(Paragraph(f"  • {tip}", styles["Body"]))
    return items


def _score_badge(score: float) -> str:
    if score >= 85:
        return "Excellent ✅"
    elif score >= 70:
        return "Good 👍"
    elif score >= 55:
        return "Fair ⚠️"
    else:
        return "Poor 🔴"
