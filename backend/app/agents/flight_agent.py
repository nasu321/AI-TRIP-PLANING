"""
Flight Intelligence Agent — fetches flights and computes affordability.
"""
import logging
from app.agents.state import TravelPlanState
from app.services.flight_service import get_flights

logger = logging.getLogger(__name__)


async def flight_agent(state: TravelPlanState) -> TravelPlanState:
    """Fetch flight options and score affordability."""
    logger.info(f"[FlightAgent] Searching flights to: {state['destination']}")
    try:
        flights = await get_flights(
            origin="User's Origin",
            destination=state["destination"],
            start_date=state.get("start_date"),
            budget_usd=state.get("budget_usd"),
        )
        state["flights"] = flights
        state.setdefault("completed_agents", []).append("flight_agent")
        logger.info(f"[FlightAgent] ✅ Found {len(flights)} flight options")
    except Exception as e:
        logger.error(f"[FlightAgent] ❌ Error: {e}")
        state.setdefault("errors", []).append(f"flight_agent: {str(e)}")
    return state
