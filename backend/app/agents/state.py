"""
Shared state definition for the LangGraph multi-agent travel planning system.
All agents read from and write to this shared state object.
"""
from typing import TypedDict, Optional, List, Dict, Any
from app.schemas import (
    WeatherResult, HotelResult, FlightResult,
    BudgetBreakdown, ReviewInsight, ItineraryDay,
    AttractionResult, TravelScore, NearbyService
)


class TravelPlanState(TypedDict, total=False):
    """
    Shared state passed between all agents in the LangGraph pipeline.
    Each agent reads relevant fields and writes back its results.
    """
    # Input fields (set by user)
    session_id: str
    destination: str
    start_date: Optional[str]
    end_date: Optional[str]
    duration_days: int
    budget_usd: float
    currency: str
    travelers_count: int
    travel_purpose: Optional[str]
    preferences: Dict[str, Any]
    user_persona: Optional[str]

    # Agent outputs
    weather_result: Optional[WeatherResult]
    hotels: Optional[List[HotelResult]]
    flights: Optional[List[FlightResult]]
    budget: Optional[BudgetBreakdown]
    review_insights: Optional[List[ReviewInsight]]
    attractions: Optional[List[AttractionResult]]
    nearby_services: Optional[List[NearbyService]]
    itinerary: Optional[List[ItineraryDay]]
    travel_score: Optional[TravelScore]
    personalized_tips: Optional[List[str]]
    agent_reasoning: Optional[str]

    # Error tracking
    errors: List[str]
    completed_agents: List[str]
