"""
Trip ORM models — stores trip records, hotels, flights, and itinerary.
"""
from sqlalchemy import (
    Column, Integer, String, Float, Date, DateTime,
    ForeignKey, Text, JSON, Boolean
)
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class Trip(Base):
    __tablename__ = "trips"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # Destination info
    destination = Column(String(200), nullable=False)
    country = Column(String(100), nullable=True)
    destination_lat = Column(Float, nullable=True)
    destination_lon = Column(Float, nullable=True)

    # Travel dates
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    duration_days = Column(Integer, nullable=True)

    # Budget
    budget_usd = Column(Float, nullable=True)
    currency = Column(String(10), default="USD")
    estimated_cost_usd = Column(Float, nullable=True)

    # Travel details
    travelers_count = Column(Integer, default=1)
    travel_purpose = Column(String(100), nullable=True)

    # AI-generated travel score (0-100)
    travel_score = Column(Float, nullable=True)

    # Status
    status = Column(String(30), default="pending")  # pending, completed, failed

    # Full AI result as JSON
    full_result = Column(JSON, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="trips")
    hotels = relationship("TripHotel", back_populates="trip", cascade="all, delete-orphan")
    flights = relationship("TripFlight", back_populates="trip", cascade="all, delete-orphan")
    itinerary = relationship("TripItinerary", back_populates="trip", cascade="all, delete-orphan")
    reports = relationship("Report", back_populates="trip", cascade="all, delete-orphan")


class TripHotel(Base):
    __tablename__ = "trip_hotels"

    id = Column(Integer, primary_key=True, index=True)
    trip_id = Column(Integer, ForeignKey("trips.id", ondelete="CASCADE"), nullable=False)

    hotel_name = Column(String(200), nullable=False)
    address = Column(String(300), nullable=True)
    price_per_night_usd = Column(Float, nullable=True)
    rating = Column(Float, nullable=True)
    sentiment_score = Column(Float, nullable=True)
    recommendation_score = Column(Float, nullable=True)
    pros = Column(JSON, nullable=True)
    cons = Column(JSON, nullable=True)
    image_url = Column(String(500), nullable=True)
    amenities = Column(JSON, nullable=True)
    is_recommended = Column(Boolean, default=False)

    trip = relationship("Trip", back_populates="hotels")


class TripFlight(Base):
    __tablename__ = "trip_flights"

    id = Column(Integer, primary_key=True, index=True)
    trip_id = Column(Integer, ForeignKey("trips.id", ondelete="CASCADE"), nullable=False)

    airline = Column(String(100), nullable=True)
    flight_number = Column(String(20), nullable=True)
    origin = Column(String(100), nullable=True)
    destination = Column(String(100), nullable=True)
    price_usd = Column(Float, nullable=True)
    duration_hours = Column(Float, nullable=True)
    departure_time = Column(String(50), nullable=True)
    arrival_time = Column(String(50), nullable=True)
    stops = Column(Integer, default=0)
    is_cheapest = Column(Boolean, default=False)

    trip = relationship("Trip", back_populates="flights")


class TripItinerary(Base):
    __tablename__ = "trip_itinerary"

    id = Column(Integer, primary_key=True, index=True)
    trip_id = Column(Integer, ForeignKey("trips.id", ondelete="CASCADE"), nullable=False)

    day_number = Column(Integer, nullable=False)
    date = Column(Date, nullable=True)
    title = Column(String(200), nullable=True)
    activities = Column(JSON, nullable=True)
    meals = Column(JSON, nullable=True)
    accommodation = Column(String(200), nullable=True)
    estimated_daily_cost = Column(Float, nullable=True)
    notes = Column(Text, nullable=True)

    trip = relationship("Trip", back_populates="itinerary")
