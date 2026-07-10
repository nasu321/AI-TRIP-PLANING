"""
LangGraph Orchestrator — defines the multi-agent graph and execution pipeline.
Agents run in parallel where possible, then the planner synthesizes results.
"""
import asyncio
import logging
from datetime import date
from typing import Optional, Dict, Any

from langgraph.graph import StateGraph, END

from app.agents.state import TravelPlanState
from app.agents.weather_agent import weather_agent
from app.agents.recommendation_agent import recommendation_agent
from app.agents.flight_agent import flight_agent
from app.agents.review_agent import review_agent
from app.agents.budget_agent import budget_agent
from app.agents.planner_agent import planner_agent

logger = logging.getLogger(__name__)


async def parallel_data_agents(state: TravelPlanState) -> TravelPlanState:
    """
    Run weather, recommendation, and flight agents concurrently.
    This significantly reduces total execution time.
    """
    logger.info("[Graph] Running parallel data collection agents...")
    results = await asyncio.gather(
        weather_agent(dict(state)),
        recommendation_agent(dict(state)),
        flight_agent(dict(state)),
        return_exceptions=True
    )

    # Merge results back into state
    for result in results:
        if isinstance(result, Exception):
            logger.error(f"Parallel agent error: {result}")
            state.setdefault("errors", []).append(str(result))
        elif isinstance(result, dict):
            for key in ["weather_result", "hotels", "attractions", "nearby_services", "flights"]:
                if key in result and result[key] is not None:
                    state[key] = result[key]
            for key in ["completed_agents", "errors"]:
                if key in result:
                    state.setdefault(key, [])
                    state[key] = list(set(state[key] + result[key]))

    return state


async def sequential_analysis_agents(state: TravelPlanState) -> TravelPlanState:
    """
    Run review and budget agents after data is collected.
    These depend on hotels/flights output from the parallel phase.
    """
    logger.info("[Graph] Running sequential analysis agents...")
    state = await review_agent(state)
    state = await budget_agent(state)
    return state


def build_travel_graph() -> StateGraph:
    """
    Build the LangGraph StateGraph for the travel planning pipeline.

    Flow:
    START → parallel_data_agents → sequential_analysis_agents → planner_agent → END
    """
    graph = StateGraph(TravelPlanState)

    graph.add_node("parallel_data", parallel_data_agents)
    graph.add_node("analysis", sequential_analysis_agents)
    graph.add_node("planner", planner_agent)

    graph.set_entry_point("parallel_data")
    graph.add_edge("parallel_data", "analysis")
    graph.add_edge("analysis", "planner")
    graph.add_edge("planner", END)

    return graph.compile()


# Compiled graph singleton
travel_graph = build_travel_graph()


async def run_travel_plan(
    session_id: str,
    destination: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    budget_usd: Optional[float] = None,
    currency: str = "USD",
    travelers_count: int = 1,
    travel_purpose: Optional[str] = None,
    preferences: Optional[Dict[str, Any]] = None,
) -> TravelPlanState:
    """
    Entry point to execute the full travel planning pipeline.
    Returns complete state with all agent results.
    """
    # Calculate duration
    duration_days = 7  # default
    if start_date and end_date:
        try:
            start = date.fromisoformat(str(start_date))
            end = date.fromisoformat(str(end_date))
            duration_days = max(1, (end - start).days)
        except Exception:
            pass

    initial_state: TravelPlanState = {
        "session_id": session_id,
        "destination": destination,
        "start_date": str(start_date) if start_date else None,
        "end_date": str(end_date) if end_date else None,
        "duration_days": duration_days,
        "budget_usd": budget_usd or 0,
        "currency": currency,
        "travelers_count": travelers_count,
        "travel_purpose": travel_purpose,
        "preferences": preferences or {},
        "errors": [],
        "completed_agents": [],
    }

    logger.info(f"[TravelGraph] 🚀 Starting pipeline for: {destination}")
    final_state = await travel_graph.ainvoke(initial_state)
    logger.info(f"[TravelGraph] ✅ Pipeline complete. Agents: {final_state.get('completed_agents', [])}")

    if final_state.get("errors"):
        logger.warning(f"[TravelGraph] ⚠️ Errors: {final_state['errors']}")

    return final_state
