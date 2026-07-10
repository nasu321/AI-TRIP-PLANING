"""
User ORM model — stores profile, travel persona, and preferences.
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(100), unique=True, index=True, nullable=False)
    name = Column(String(100), nullable=True, default="Traveler")
    email = Column(String(200), nullable=True)
    phone = Column(String(30), nullable=True)

    # Travel persona classification
    persona = Column(String(50), nullable=True)  # e.g., "Adventure", "Luxury", "Budget", "Cultural"

    # Preferences stored as JSON
    preferences = Column(JSON, nullable=True, default=dict)
    # {
    #   "preferred_climate": "tropical",
    #   "accommodation_type": "hotel",
    #   "travel_style": "relaxed",
    #   "dietary": "vegetarian",
    #   "activities": ["hiking", "museums"]
    # }

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    trips = relationship("Trip", back_populates="user", cascade="all, delete-orphan")
