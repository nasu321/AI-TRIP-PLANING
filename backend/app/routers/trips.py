"""
Trips router — handles trip planning and retrieval endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime
import logging

from app.database import get_db
from app.models.user import User
from app.models.trip import Trip, TripHotel, TripFlight, TripItinerary
from app.schemas import TripPlanRequest, TripPlanResult, SuccessResponse
from app.agents.graph import run_travel_plan

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/trips", tags=["Trips"])


async def get_or_create_user(session_id: str, db: AsyncSession) -> User:
    """Get existing user by session_id, or create a new one."""
    result = await db.execute(select(User).where(User.session_id == session_id))
    user = result.scalar_one_or_none()
    if not user:
        user = User(session_id=session_id)
        db.add(user)
        await db.commit()
        await db.refresh(user)
    return user


@router.post("/plan", response_model=TripPlanResult)
async def plan_trip(
    request: TripPlanRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Execute the full multi-agent travel planning pipeline.
    Returns comprehensive trip data including hotels, flights, weather, budget, and itinerary.
    """
    logger.info(f"[API] Trip plan request: {request.destination} by {request.session_id}")

    # Get or create user
    user = await get_or_create_user(request.session_id, db)

    # Create trip record
    trip = Trip(
        user_id=user.id,
        destination=request.destination,
        start_date=request.start_date,
        end_date=request.end_date,
        budget_usd=request.budget_usd,
        currency=request.currency,
        travelers_count=request.travelers_count,
        travel_purpose=request.travel_purpose,
        status="pending",
    )
    db.add(trip)
    await db.commit()
    await db.refresh(trip)

    try:
        # Run the multi-agent pipeline
        state = await run_travel_plan(
            session_id=request.session_id,
            destination=request.destination,
            start_date=str(request.start_date) if request.start_date else None,
            end_date=str(request.end_date) if request.end_date else None,
            budget_usd=request.budget_usd,
            currency=request.currency,
            travelers_count=request.travelers_count,
            travel_purpose=request.travel_purpose,
            preferences=request.preferences,
        )

        # Build result
        result = TripPlanResult(
            trip_id=trip.id,
            destination=request.destination,
            travel_score=state["travel_score"],
            city_rating=round((state.get("travel_score").total / 10.0), 1) if state.get("travel_score") else 0.0,
            weather=state["weather_result"],
            recommended_hotels=state.get("hotels", []),
            flights=state.get("flights", []),
            budget=state["budget"],
            review_insights=state.get("review_insights", []),
            itinerary=state.get("itinerary", []),
            attractions=state.get("attractions", []),
            nearby_services=state.get("nearby_services", []),
            personalized_tips=state.get("personalized_tips", []),
            agent_reasoning=state.get("agent_reasoning", ""),
            created_at=datetime.utcnow().isoformat(),
        )

        # Update trip record with results
        trip.travel_score = result.travel_score.total
        trip.estimated_cost_usd = result.budget.total_estimated_usd
        trip.duration_days = state.get("duration_days", 7)
        trip.status = "completed"
        trip.full_result = result.model_dump()

        # Update user persona
        if state.get("user_persona"):
            user.persona = state["user_persona"]

        await db.commit()

        return result

    except Exception as e:
        trip.status = "failed"
        await db.commit()
        logger.error(f"Trip planning failed: {e}")
        raise HTTPException(status_code=500, detail=f"Trip planning failed: {str(e)}")


@router.get("/{trip_id}", response_model=TripPlanResult)
async def get_trip(trip_id: int, db: AsyncSession = Depends(get_db)):
    """Retrieve a previously planned trip by ID."""
    result = await db.execute(select(Trip).where(Trip.id == trip_id))
    trip = result.scalar_one_or_none()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    if not trip.full_result:
        raise HTTPException(status_code=404, detail="Trip result not available")

    return TripPlanResult(**trip.full_result)


@router.get("/user/{session_id}", response_model=list)
async def get_user_trips(session_id: str, db: AsyncSession = Depends(get_db)):
    """Get trip history for a user session."""
    user = await get_or_create_user(session_id, db)
    result = await db.execute(
        select(Trip).where(Trip.user_id == user.id).order_by(Trip.created_at.desc()).limit(10)
    )
    trips = result.scalars().all()
    return [
        {
            "trip_id": t.id,
            "destination": t.destination,
            "travel_score": t.travel_score,
            "budget_usd": t.budget_usd,
            "estimated_cost_usd": t.estimated_cost_usd,
            "status": t.status,
            "created_at": t.created_at.isoformat() if t.created_at else None,
        }
        for t in trips
    ]
