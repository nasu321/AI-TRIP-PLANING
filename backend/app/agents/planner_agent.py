"""
Planner Agent — orchestrates the final itinerary and travel score computation.
Uses LLM if configured, otherwise uses rule-based planning.
"""
import logging
import asyncio
from datetime import date, timedelta
from typing import List, Optional
from app.agents.state import TravelPlanState
from app.schemas import ItineraryDay, TravelScore
from app.services.personalization_service import classify_persona, generate_personalized_tips
from app.config import settings

logger = logging.getLogger(__name__)


def _compute_travel_score(state: TravelPlanState) -> TravelScore:
    """Compute composite travel score from agent outputs."""
    weather = state.get("weather_result")
    budget = state.get("budget")
    hotels = state.get("hotels", [])
    flights = state.get("flights", [])
    reviews = state.get("review_insights", [])

    weather_score = weather.suitability_score if weather else 70.0

    budget_score = budget.budget_fit_score if budget else 70.0

    hotel_score = 0.0
    if hotels:
        hotel_score = sum(h.recommendation_score for h in hotels[:3]) / min(len(hotels), 3)

    sentiment_score = 0.0
    if reviews:
        sentiment_score = sum(r.positive_pct for r in reviews) / len(reviews)

    flight_score = 0.0
    if flights:
        flight_score = sum(f.affordability_score for f in flights) / len(flights)

    total = round(
        weather_score * 0.20 +
        budget_score * 0.25 +
        hotel_score * 0.25 +
        sentiment_score * 0.20 +
        flight_score * 0.10,
        1
    )

    if total >= 85:
        label = "Excellent ⭐⭐⭐⭐⭐"
        explanation = f"Outstanding conditions! {state['destination']} scores extremely high across all categories."
    elif total >= 70:
        label = "Great 🌟🌟🌟🌟"
        explanation = f"Strong overall score. {state['destination']} offers great value with minor trade-offs."
    elif total >= 55:
        label = "Good 👍👍👍"
        explanation = f"Solid choice. Some areas to watch — check budget and weather flexibility."
    else:
        label = "Fair ⚠️"
        explanation = f"Manageable with planning. Consider adjusting budget or dates for better results."

    return TravelScore(
        total=total,
        weather_score=round(weather_score, 1),
        budget_score=round(budget_score, 1),
        hotel_score=round(hotel_score, 1),
        sentiment_score=round(sentiment_score, 1),
        flight_score=round(flight_score, 1),
        label=label,
        explanation=explanation,
    )


def _build_itinerary(state: TravelPlanState) -> List[ItineraryDay]:
    """Build structured day-by-day itinerary with tourist spots and weather per day."""
    duration = state.get("duration_days", 7)
    destination = state["destination"]
    attractions = state.get("attractions", [])
    hotels = state.get("hotels", [])
    budget = state.get("budget")
    weather_forecast = []
    weather = state.get("weather_result")
    if weather:
        weather_forecast = weather.forecast

    top_hotel = hotels[0].hotel_name if hotels else f"{destination} Central Hotel"
    daily_cost = (budget.total_estimated_usd / duration) if budget and duration else 120

    # Keep attraction objects instead of strings
    attr_objects = list(attractions) if attractions else []

    # Day structure templates: (title, morning, afternoon, evening)
    day_structures = [
        ("Arrival & Orientation",
         ["Airport pickup & hotel check-in", "Freshen up & rest"],
         ["Neighbourhood orientation walk", "Visit nearest attraction"],
         ["Welcome dinner at local restaurant", "Evening stroll"]),
        ("City Highlights",
         ["Guided walking tour of city center", "Major landmark visit"],
         ["Local lunch & street food experience", "Visit top-rated attraction"],
         ["Sunset viewpoint", "Traditional dinner"]),
        ("Cultural Immersion",
         ["Museum visit", "Historical quarter exploration"],
         ["Art gallery or cultural centre", "Local crafts market"],
         ["Cultural performance or show", "Fine dining experience"]),
        ("Day Excursion",
         ["Early start — day trip to scenic location", "Nature park or viewpoint"],
         ["Outdoor lunch with scenic views", "Exploration & photography"],
         ["Return to hotel", "Relaxed dinner"]),
        ("Local Experiences",
         ["Morning market visit", "Cooking class or food tour"],
         ["Free time for souvenir shopping", "Local café visit"],
         ["Farewell dinner", "Evening leisure"]),
        ("Leisure & Wellness",
         ["Hotel breakfast", "Spa or pool morning"],
         ["Shopping district", "Café lunch"],
         ["Sunset cruise or rooftop bar", "Gourmet dinner"]),
        ("Departure Day",
         ["Final hotel breakfast", "Last-minute souvenir shopping"],
         ["Pack & check-out", "Visit missed attraction if time allows"],
         ["Airport transfer", "Safe travels!"]),
    ]

    itinerary = []
    for day_num in range(1, duration + 1):
        tmpl_idx = (day_num - 1) % len(day_structures)
        title, morning, afternoon, evening = day_structures[tmpl_idx]

        # Distribute actual attractions based on best time to visit
        morning_attrs = []
        afternoon_attrs = []
        evening_attrs = []
        day_attractions = []
        
        if attr_objects:
            primary_idx = (day_num - 1) % len(attr_objects)
            primary_attr = attr_objects[primary_idx]
            time_pref = getattr(primary_attr, "best_time_to_visit", "Afternoon").lower()
            p_fee = getattr(primary_attr, "entry_fee_usd", 0)
            p_fee_str = f"${p_fee:.2f}" if p_fee else "Free"
            name_with_city = f"🎟️ {primary_attr.name} ({destination.split(',')[0]}) [Entry: {p_fee_str} | Book: Walk-in/Online]"
            
            if "morning" in time_pref: morning_attrs.append(name_with_city)
            elif "evening" in time_pref or "sunset" in time_pref: evening_attrs.append(name_with_city)
            else: afternoon_attrs.append(name_with_city)
            
            day_attractions.append(primary_attr.name)
            
            if 1 < day_num < duration and len(attr_objects) > 1:
                secondary_idx = day_num % len(attr_objects)
                if secondary_idx != primary_idx:
                    sec_attr = attr_objects[secondary_idx]
                    sec_time_pref = getattr(sec_attr, "best_time_to_visit", "Afternoon").lower()
                    s_fee = getattr(sec_attr, "entry_fee_usd", 0)
                    s_fee_str = f"${s_fee:.2f}" if s_fee else "Free"
                    sec_name_with_city = f"🎟️ {sec_attr.name} ({destination.split(',')[0]}) [Entry: {s_fee_str} | Book: Walk-in/Online]"
                    
                    if "morning" in sec_time_pref: morning_attrs.append(sec_name_with_city)
                    elif "evening" in sec_time_pref or "sunset" in sec_time_pref: evening_attrs.append(sec_name_with_city)
                    else: afternoon_attrs.append(sec_name_with_city)
                    
                    day_attractions.append(sec_attr.name)

        # Get weather for this day
        weather_info = None
        if weather_forecast and day_num <= len(weather_forecast):
            wd = weather_forecast[day_num - 1]
            weather_info = f"{wd.icon} {wd.condition} | {wd.temp_high_c:.0f}C / {wd.temp_low_c:.0f}C"
            if wd.precipitation_mm > 10:
                afternoon = ["Indoor museum visit (rain day)", "Shopping centre", "Cafe & gallery time"]
            elif wd.temp_high_c > 35:
                afternoon = ["Early sightseeing before noon heat", "Afternoon indoor rest", "Evening outdoor exploration"]

        # Meals
        meal_options = [
            ["Hotel breakfast", "Local street food lunch", "Restaurant dinner"],
            ["Buffet breakfast", "Cafe lunch", "Traditional dinner"],
            ["Continental breakfast", "Market food lunch", "Fine dining dinner"],
            ["Hotel breakfast", "Packed picnic lunch", "Hotel dinner"],
        ]
        meals = meal_options[(day_num - 1) % len(meal_options)]

        # Override first and last day
        if day_num == 1:
            title = f"Arrival in {destination}"
            morning = [f"Arrive at {destination}", "Hotel check-in & freshen up"]
            afternoon = ["Neighbourhood walk", day_attractions[0] if day_attractions else "Welcome orientation"]
            evening = ["Welcome dinner at local restaurant", "Early rest"]
        elif day_num == duration:
            title = "Farewell & Departure"
            morning = ["Hotel breakfast", "Final packing"]
            afternoon = [day_attractions[0] if day_attractions else "Last sightseeing", "Souvenir shopping"]
            evening = ["Airport transfer", "Depart — safe travels!"]

        # Inject scheduled attractions into the lists if applicable
        if day_num != 1 and day_num != duration:
            morning.extend(morning_attrs)
            afternoon.extend(afternoon_attrs)
            evening.extend(evening_attrs)

        all_activities = [
            f"MORNING: {' | '.join(morning)}",
            f"AFTERNOON: {' | '.join(afternoon)}",
            f"EVENING: {' | '.join(evening)}",
        ]

        notes = f"Tourist spots: {', '.join(day_attractions)}" if day_attractions else ""
        if weather_info:
            notes += f" || Weather: {weather_info}"

        itinerary.append(ItineraryDay(
            day_number=day_num,
            title=title,
            activities=all_activities,
            meals=meals,
            accommodation=top_hotel if day_num < duration else "Check-out by 12:00",
            estimated_daily_cost_usd=round(daily_cost, 0),
            notes=notes,
        ))

    return itinerary


def _build_agent_reasoning(state: TravelPlanState) -> str:
    """Generate explainable reasoning text for the AI decision."""
    dest = state["destination"]
    budget = state.get("budget")
    weather = state.get("weather_result")
    hotels = state.get("hotels", [])
    score = state.get("travel_score")

    top_hotel = hotels[0].hotel_name if hotels else "a highly rated hotel"
    top_rec_score = hotels[0].recommendation_score if hotels else 0

    reasoning = (
        f"After analyzing {dest} across 6 AI agent dimensions — "
        f"weather conditions, hotel quality, flight availability, budget compatibility, "
        f"review sentiment, and personalization — here is the comprehensive assessment:\n\n"
    )

    if weather:
        reasoning += f"🌤️ WEATHER: {dest} shows {weather.suitability_label} conditions with a "
        reasoning += f"suitability score of {weather.suitability_score:.0f}/100. {weather.best_time_note}\n\n"

    if hotels:
        reasoning += f"🏨 HOTELS: Top recommendation is '{top_hotel}' with a weighted "
        reasoning += f"recommendation score of {top_rec_score:.0f}/100, balancing rating, budget fit, and sentiment.\n\n"

    if budget:
        reasoning += f"💰 BUDGET: Total estimated cost is ${budget.total_estimated_usd:,.0f}. "
        reasoning += f"Budget assessment: {budget.budget_fit_label}\n\n"

    if score:
        reasoning += f"⭐ FINAL VERDICT: Overall Travel Score of {score.total:.0f}/100 — {score.label}\n"
        reasoning += score.explanation

    return reasoning


async def planner_agent(state: TravelPlanState) -> TravelPlanState:
    """
    Master planner that synthesizes all agent outputs into:
    - Final itinerary
    - Travel score
    - Personalized tips
    - Explainable reasoning
    """
    logger.info(f"[PlannerAgent] Building final plan for: {state['destination']}")
    try:
        # Compute travel score
        travel_score = _compute_travel_score(state)
        state["travel_score"] = travel_score

        # Build itinerary
        itinerary = _build_itinerary(state)
        state["itinerary"] = itinerary

        # Classify persona and generate tips
        persona = classify_persona(
            preferences=state.get("preferences", {}),
            budget_usd=state.get("budget_usd"),
            travel_purpose=state.get("travel_purpose"),
        )
        state["user_persona"] = persona.value

        tips = generate_personalized_tips(
            persona=persona,
            destination=state["destination"],
            budget_usd=state.get("budget_usd"),
        )
        state["personalized_tips"] = tips

        # Build reasoning
        reasoning = _build_agent_reasoning(state)
        state["agent_reasoning"] = reasoning

        state.setdefault("completed_agents", []).append("planner_agent")
        logger.info(f"[PlannerAgent] ✅ Plan complete. Score: {travel_score.total}")

    except Exception as e:
        logger.error(f"[PlannerAgent] ❌ Error: {e}")
        state.setdefault("errors", []).append(f"planner_agent: {str(e)}")

    return state
