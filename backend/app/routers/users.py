"""
Users router — user profile and preference management.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.database import get_db
from app.models.user import User
from app.models.trip import Trip
from app.schemas import UserPreferences, UserProfile, SuccessResponse

router = APIRouter(prefix="/api/users", tags=["Users"])


@router.get("/{session_id}", response_model=UserProfile)
async def get_user_profile(session_id: str, db: AsyncSession = Depends(get_db)):
    """Get user profile by session ID."""
    result = await db.execute(select(User).where(User.session_id == session_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Count trips
    count_result = await db.execute(
        select(func.count()).where(Trip.user_id == user.id, Trip.status == "completed")
    )
    trip_count = count_result.scalar() or 0

    return UserProfile(
        session_id=user.session_id,
        name=user.name,
        persona=user.persona,
        preferences=user.preferences or {},
        trip_count=trip_count,
        created_at=user.created_at.isoformat() if user.created_at else "",
    )


@router.put("/{session_id}/preferences", response_model=SuccessResponse)
async def update_preferences(
    session_id: str,
    preferences: UserPreferences,
    db: AsyncSession = Depends(get_db),
):
    """Update user preferences."""
    result = await db.execute(select(User).where(User.session_id == session_id))
    user = result.scalar_one_or_none()

    if not user:
        user = User(session_id=session_id)
        db.add(user)

    pref_data = preferences.model_dump(exclude_none=True)
    if "name" in pref_data:
        user.name = pref_data.pop("name")
    if "email" in pref_data:
        user.email = pref_data.pop("email")
    if "phone" in pref_data:
        user.phone = pref_data.pop("phone")

    user.preferences = {**(user.preferences or {}), **pref_data}
    await db.commit()

    return SuccessResponse(message="Preferences updated successfully")
