"""
Weather Agent — fetches and analyzes weather data for the destination.
"""
import logging
from app.agents.state import TravelPlanState
from app.services.weather_service import get_weather

logger = logging.getLogger(__name__)


async def weather_agent(state: TravelPlanState) -> TravelPlanState:
    """
    Fetch weather forecast and compute suitability score.
    Updates state with weather_result.
    """
    logger.info(f"[WeatherAgent] Processing weather for: {state['destination']}")
    try:
        weather = await get_weather(
            destination=state["destination"],
            start_date=state.get("start_date"),
        )
        state["weather_result"] = weather
        state.setdefault("completed_agents", []).append("weather_agent")
        logger.info(f"[WeatherAgent] ✅ Suitability: {weather.suitability_score}/100")
    except Exception as e:
        logger.error(f"[WeatherAgent] ❌ Error: {e}")
        state.setdefault("errors", []).append(f"weather_agent: {str(e)}")
    return state
