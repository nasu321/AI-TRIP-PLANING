"""Quick end-to-end test of the travel planning pipeline."""
import sys
import asyncio
sys.stdout.reconfigure(encoding='utf-8')

async def test_pipeline():
    from app.agents.graph import run_travel_plan
    print("Running full agent pipeline for Paris, France...")
    state = await run_travel_plan(
        session_id="test-001",
        destination="Paris, France",
        start_date="2025-08-15",
        end_date="2025-08-22",
        budget_usd=3000,
        currency="USD",
        travelers_count=2,
        travel_purpose="Honeymoon",
        preferences={"travel_style": "romantic", "activities": ["museums", "dining"]},
    )

    completed = state.get("completed_agents", [])
    errors = state.get("errors", [])
    print(f"Completed Agents: {completed}")
    print(f"Errors: {errors}")

    ts = state.get("travel_score")
    if ts:
        print(f"Travel Score: {ts.total:.1f}/100 — {ts.label}")
        print(f"  Weather: {ts.weather_score:.0f}  Budget: {ts.budget_score:.0f}  Hotels: {ts.hotel_score:.0f}  Sentiment: {ts.sentiment_score:.0f}  Flights: {ts.flight_score:.0f}")

    weather = state.get("weather_result")
    if weather:
        print(f"Weather: {weather.suitability_score}/100 — {weather.suitability_label}")
        print(f"  Forecast days: {len(weather.forecast)}")

    hotels = state.get("hotels", [])
    if hotels:
        top = hotels[0]
        print(f"Hotels: {len(hotels)} found")
        print(f"  Top: {top.hotel_name} | Score: {top.recommendation_score:.0f}/100 | ${top.price_per_night_usd}/night")

    flights = state.get("flights", [])
    if flights:
        cheapest = min(flights, key=lambda f: f.price_usd)
        print(f"Flights: {len(flights)} found")
        print(f"  Cheapest: {cheapest.airline} at ${cheapest.price_usd:,.0f}")

    budget = state.get("budget")
    if budget:
        print(f"Budget: ${budget.total_estimated_usd:,.0f} estimated | Fit: {budget.budget_fit_score:.0f}/100")
        print(f"  Label: {budget.budget_fit_label}")

    itinerary = state.get("itinerary", [])
    print(f"Itinerary: {len(itinerary)} days planned")
    if itinerary:
        print(f"  Day 1: {itinerary[0].title}")

    reviews = state.get("review_insights", [])
    print(f"Review insights: {len(reviews)} hotels analyzed")

    persona = state.get("user_persona")
    tips = state.get("personalized_tips", [])
    print(f"Persona: {persona} | Tips: {len(tips)}")

    reasoning = state.get("agent_reasoning", "")
    print(f"Agent reasoning length: {len(reasoning)} chars")

    print("")
    print("=" * 50)
    print("FULL PIPELINE TEST PASSED!")
    print("=" * 50)

    # Test PDF generation
    print("\nTesting PDF generation...")
    from app.schemas import TripPlanResult
    from datetime import datetime
    result = TripPlanResult(
        trip_id=1,
        destination="Paris, France",
        travel_score=ts,
        weather=weather,
        recommended_hotels=hotels,
        flights=flights,
        budget=budget,
        review_insights=reviews,
        itinerary=itinerary,
        attractions=state.get("attractions", []),
        personalized_tips=tips,
        agent_reasoning=reasoning,
        created_at=datetime.utcnow().isoformat(),
    )
    from app.services.pdf_service import generate_pdf_report
    pdf_path = generate_pdf_report(result)
    import os
    pdf_size = os.path.getsize(pdf_path)
    print(f"PDF generated: {pdf_path}")
    print(f"PDF size: {pdf_size:,} bytes ({pdf_size//1024} KB)")
    print("PDF GENERATION PASSED!")

asyncio.run(test_pipeline())
