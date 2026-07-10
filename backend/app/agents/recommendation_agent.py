"""
Recommendation Agent — fetches hotels, attractions, nearby services, applies weighted scoring.
"""
import logging
from app.agents.state import TravelPlanState
from app.services.places_service import get_hotels, get_attractions, get_review_insights, get_nearby_services

logger = logging.getLogger(__name__)


async def recommendation_agent(state: TravelPlanState) -> TravelPlanState:
    """
    Fetch hotels, attractions, and nearby services. Apply weighted scoring, rank results.
    Scoring formula:
      rating * 0.30 + budget_fit * 0.25 + sentiment * 0.25 + popularity * 0.10 + weather_fit * 0.10
    """
    logger.info(f"[RecommendationAgent] Finding hotels/attractions/services for: {state['destination']}")
    try:
        budget = state.get("budget_usd") or 0
        duration = state.get("duration_days") or 7
        budget_per_night = (budget * 0.35 / duration) if budget and duration else None

        hotels      = await get_hotels(state["destination"], budget_per_night)
        
        # Add rank badges and AI reasoning for UI redesign
        badges = ["#1 Best Match", "#2 Value Choice", "#3 Cultural Pick", "#4 Comfort Stay"]
        for i, h in enumerate(hotels):
            h.rank_badge = badges[i] if i < len(badges) else f"#{i+1} Great Option"
            h.ai_reasoning = f"Matches your preference for a {'budget' if h.budget_fit_score > 80 else 'premium'} stay. Highly rated for its {h.pros[0].lower()} and {h.pros[1].lower()}."
            
        attractions = await get_attractions(state["destination"])
        services    = await get_nearby_services(state["destination"])

        state["hotels"]          = hotels
        state["attractions"]     = attractions
        state["nearby_services"] = services
        state.setdefault("completed_agents", []).append("recommendation_agent")
        logger.info(
            f"[RecommendationAgent] ✅ Found {len(hotels)} hotels, "
            f"{len(attractions)} attractions, {len(services)} nearby services"
        )
    except Exception as e:
        logger.error(f"[RecommendationAgent] ❌ Error: {e}")
        state.setdefault("errors", []).append(f"recommendation_agent: {str(e)}")
    return state

