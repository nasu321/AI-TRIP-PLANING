"""
Review Analyzer Agent — sentiment analysis on hotel reviews.
"""
import logging
from app.agents.state import TravelPlanState
from app.services.places_service import get_review_insights

logger = logging.getLogger(__name__)


async def review_agent(state: TravelPlanState) -> TravelPlanState:
    """
    Analyze hotel reviews to compute:
    - Positivity percentage
    - Pros / Cons extraction
    - Recurring complaint detection
    - AI review summary
    """
    logger.info(f"[ReviewAgent] Analyzing reviews for {state['destination']}")
    try:
        hotels = state.get("hotels", [])
        if not hotels:
            state.setdefault("errors", []).append("review_agent: No hotels to analyze")
            return state

        insights = await get_review_insights(state["destination"], hotels)
        state["review_insights"] = insights
        state.setdefault("completed_agents", []).append("review_agent")
        logger.info(f"[ReviewAgent] ✅ Analyzed {len(insights)} hotel reviews")
    except Exception as e:
        logger.error(f"[ReviewAgent] ❌ Error: {e}")
        state.setdefault("errors", []).append(f"review_agent: {str(e)}")
    return state
