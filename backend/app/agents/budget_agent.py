"""
Budget Agent — calculates total trip cost using real Numbeo cost-of-living data.

Data sources:
  - cost_of_living.csv  (Numbeo Cost of Living Index 2024)
  - international_hotel_prices.csv (Numbeo/Booking.com/STR Global)
  - flight_price_index.csv (IATA Economics 2024)
"""
import logging
from typing import List
from app.agents.state import TravelPlanState
from app.schemas import BudgetBreakdown, HotelResult, FlightResult
from app.services.data_manager import data_manager

logger = logging.getLogger(__name__)


def _cheapest_flight_price(flights: List[FlightResult]) -> float:
    if not flights:
        return 800.0
    return min(f.price_usd for f in flights)


def _cheapest_hotel_price(hotels: List[HotelResult]) -> float:
    if not hotels:
        return 120.0
    recommended = [h for h in hotels if h.is_recommended]
    pool = recommended if recommended else hotels
    return min(h.price_per_night_usd for h in pool)


def _compute_budget(
    destination: str,
    duration_days: int,
    travelers: int,
    budget_usd: float,
    flights: List[FlightResult],
    hotels: List[HotelResult],
) -> BudgetBreakdown:
    """Compute detailed budget breakdown using real cost-of-living data."""
    # Ensure DataManager is loaded
    data_manager.load()

    # ── Real data lookups ────────────────────────────────────────────────────
    col_data   = data_manager.get_cost_of_living(destination)
    hotel_data = data_manager.get_hotel_prices(destination)
    from_db    = col_data.get("data_from_db", False)

    # ── Flight cost ──────────────────────────────────────────────────────────
    flight_cost = _cheapest_flight_price(flights) * travelers

    # ── Hotel cost — use real price data ────────────────────────────────────
    hotel_nightly = _cheapest_hotel_price(hotels)
    # Cross-check with DB: if hotel service used mock and DB has real data, use DB mid price
    if hotel_data["data_from_db"] and hotel_nightly > hotel_data["luxury_usd"] * 1.5:
        hotel_nightly = hotel_data["mid_usd"]  # normalise outlier
    hotel_total = hotel_nightly * duration_days

    # ── Daily costs from Numbeo database ────────────────────────────────────
    t = travelers
    if from_db:
        daily_food      = col_data["meal_mid"] * 3 * t        # 3 meals/day
        daily_transport = col_data["local_transport_day"] * t
        daily_attr      = col_data["attraction_avg"] * t * 0.7 # not every day
        source_note     = f"Numbeo {col_data.get('source','')}"
    else:
        # Regional fallback
        dest_l = destination.lower()
        if any(k in dest_l for k in ["paris","london","zurich","oslo","stockholm","new york"]):
            daily_food, daily_transport, daily_attr = 85*t, 20*t, 50*t
        elif any(k in dest_l for k in ["bali","bangkok","vietnam","cambodia","nepal","india"]):
            daily_food, daily_transport, daily_attr = 25*t, 8*t, 20*t
        elif any(k in dest_l for k in ["dubai","singapore","hong kong"]):
            daily_food, daily_transport, daily_attr = 65*t, 15*t, 40*t
        else:
            daily_food, daily_transport, daily_attr = 50*t, 12*t, 35*t
        source_note = "Regional estimate"

    food_total       = daily_food      * duration_days
    activities_total = daily_attr      * duration_days
    transport_total  = daily_transport * duration_days
    misc             = (flight_cost + hotel_total) * 0.05  # 5% contingency

    total     = flight_cost + hotel_total + food_total + activities_total + transport_total + misc
    remaining = (budget_usd or 0) - total

    # ── Budget fit score ────────────────────────────────────────────────────
    if budget_usd and budget_usd > 0:
        ratio = total / budget_usd
        if ratio <= 0.80:
            fit_score, fit_label = 95.0, "Excellent — Well within budget ✅"
        elif ratio <= 1.0:
            fit_score, fit_label = 80.0, "Good — Fits within budget 👍"
        elif ratio <= 1.15:
            fit_score, fit_label = 60.0, "Tight — Slightly over budget ⚠️"
        else:
            fit_score, fit_label = 35.0, "Over Budget — Consider adjustments 🔴"
    else:
        fit_score, fit_label = 70.0, "No budget set — Estimates provided"

    # ── Cost-saving tips (data-driven) ──────────────────────────────────────
    tips = []
    if from_db:
        idx = col_data.get("numbeo_index", 60)
        tips.append(f"Cost index for this destination: {idx}/100 vs New York=100 (Source: {source_note})")
        if idx < 40:
            tips.append("Budget-friendly destination — your money goes further here")
            tips.append(f"Cheap meal from ~${col_data['meal_cheap']:.0f} | Mid-range ~${col_data['meal_mid']:.0f}")
        elif idx > 90:
            tips.append("Expensive city — book accommodation 60+ days in advance")
            tips.append(f"Budget for meals ~${col_data['meal_mid']:.0f}/meal at mid-range restaurants")

    if fit_score < 70:
        tips += [
            "Book flights 6-8 weeks in advance for up to 30% savings",
            "Consider nearby alternative destinations with similar experiences at lower cost",
            "Look for hotel bundles that include breakfast to reduce daily food costs",
        ]
    else:
        tips += [
            "You have budget flexibility — consider upgrading your hotel for a night or two",
            "Allocate extra to unique local experiences you'll remember forever",
        ]

    logger.info(
        f"[BudgetAgent] Cost data source: {'Numbeo DB' if from_db else 'estimate'} | "
        f"Daily food/person: ${daily_food/t:.0f} | Numbeo index: {col_data.get('numbeo_index','-')}"
    )

    return BudgetBreakdown(
        flight_cost_usd=round(flight_cost, 2),
        hotel_total_usd=round(hotel_total, 2),
        activities_total_usd=round(activities_total, 2),
        food_total_usd=round(food_total, 2),
        transport_local_usd=round(transport_total, 2),
        misc_usd=round(misc, 2),
        total_estimated_usd=round(total, 2),
        budget_remaining_usd=round(remaining, 2),
        budget_fit_score=fit_score,
        budget_fit_label=fit_label,
        cost_saving_tips=tips,
    )


async def budget_agent(state: TravelPlanState) -> TravelPlanState:
    """Calculate detailed budget breakdown using real cost-of-living database."""
    logger.info(f"[BudgetAgent] Computing budget for {state['destination']}")
    try:
        budget = _compute_budget(
            destination=state["destination"],
            duration_days=state.get("duration_days", 7),
            travelers=state.get("travelers_count", 1),
            budget_usd=state.get("budget_usd", 0),
            flights=state.get("flights", []),
            hotels=state.get("hotels", []),
        )
        state["budget"] = budget
        state.setdefault("completed_agents", []).append("budget_agent")
        logger.info(f"[BudgetAgent] ✅ Total: ${budget.total_estimated_usd:.0f}, Fit: {budget.budget_fit_score}")
    except Exception as e:
        logger.error(f"[BudgetAgent] ❌ Error: {e}")
        state.setdefault("errors", []).append(f"budget_agent: {str(e)}")
    return state
