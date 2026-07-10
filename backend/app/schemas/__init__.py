"""
Pydantic schemas for the Travel Platform API.
Defines request/response shapes for all endpoints.
"""
from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List, Dict, Any
from datetime import date, datetime
from enum import Enum


# ─────────────────────────────────────────────
# Enums
# ─────────────────────────────────────────────

class TravelPersona(str, Enum):
    ADVENTURE = "Adventure"
    LUXURY = "Luxury"
    BUDGET = "Budget"
    CULTURAL = "Cultural"
    RELAXATION = "Relaxation"
    FAMILY = "Family"
    BUSINESS = "Business"
    SOLO = "Solo"


class TripStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"


# ─────────────────────────────────────────────
# Trip Planning Request
# ─────────────────────────────────────────────

class TripPlanRequest(BaseModel):
    session_id: str = Field(..., description="User session identifier")
    destination: str = Field(..., min_length=2, max_length=200, description="Travel destination (city or country)")
    start_date: Optional[date] = Field(None, description="Trip start date")
    end_date: Optional[date] = Field(None, description="Trip end date")
    budget_usd: Optional[float] = Field(None, gt=0, description="Total budget in USD")
    currency: str = Field("USD", description="Preferred currency")
    travelers_count: int = Field(1, ge=1, le=20, description="Number of travelers")
    travel_purpose: Optional[str] = Field(None, description="Purpose: leisure, business, honeymoon, etc.")
    preferences: Optional[Dict[str, Any]] = Field(default_factory=dict)

    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "abc123",
                "destination": "Paris, France",
                "start_date": "2025-08-15",
                "end_date": "2025-08-22",
                "budget_usd": 3000,
                "currency": "USD",
                "travelers_count": 2,
                "travel_purpose": "Honeymoon",
                "preferences": {
                    "accommodation_type": "hotel",
                    "travel_style": "romantic",
                    "activities": ["museums", "dining", "sightseeing"]
                }
            }
        }


# ─────────────────────────────────────────────
# Weather Schemas
# ─────────────────────────────────────────────

class WeatherDay(BaseModel):
    date: str
    condition: str
    temp_high_c: float
    temp_low_c: float
    humidity_pct: int
    precipitation_mm: float
    wind_kmh: float
    icon: str


class WeatherResult(BaseModel):
    destination: str
    forecast: List[WeatherDay]
    suitability_score: float  # 0-100
    suitability_label: str
    packing_tips: List[str]
    best_time_note: str


# ─────────────────────────────────────────────
# Hotel / Recommendation Schemas
# ─────────────────────────────────────────────

class HotelResult(BaseModel):
    hotel_name: str
    address: Optional[str] = None
    price_per_night_usd: float
    rating: float
    sentiment_score: float  # 0-1
    recommendation_score: float  # 0-100
    budget_fit_score: float  # 0-100
    pros: List[str] = []
    cons: List[str] = []
    amenities: List[str] = []
    image_url: Optional[str] = None
    rank_badge: Optional[str] = None
    ai_reasoning: Optional[str] = None
    review_summary: str = ""
    is_recommended: bool = False


class AttractionResult(BaseModel):
    name: str
    category: str
    rating: float
    description: str
    estimated_duration_hours: float
    entry_fee_usd: float
    lat: Optional[float] = None
    lon: Optional[float] = None
    best_time_to_visit: Optional[str] = None
    image_url: Optional[str] = None
    tags: List[str] = []


class NearbyService(BaseModel):
    name: str
    service_type: str          # restaurant, cafe, hospital, atm, pharmacy, taxi, mosque, supermarket
    category_icon: str         # emoji icon
    rating: float = 0.0
    distance_m: int = 0        # metres from hotel/centre
    price_level: str = ""      # $, $$, $$$
    open_now: bool = True
    description: str = ""
    address: Optional[str] = None
    phone: Optional[str] = None
    tags: List[str] = []


# ─────────────────────────────────────────────
# Flight Schemas
# ─────────────────────────────────────────────

class FlightResult(BaseModel):
    airline: str
    flight_number: Optional[str] = None
    origin: str
    destination: str
    price_usd: float
    duration_hours: float
    departure_time: str
    arrival_time: str
    stops: int = 0
    is_cheapest: bool = False
    is_fastest: bool = False
    affordability_score: float  # 0-100


# ─────────────────────────────────────────────
# Budget Schemas
# ─────────────────────────────────────────────

class BudgetBreakdown(BaseModel):
    flight_cost_usd: float
    hotel_total_usd: float
    activities_total_usd: float
    food_total_usd: float
    transport_local_usd: float
    misc_usd: float
    total_estimated_usd: float
    budget_remaining_usd: float
    budget_fit_score: float  # 0-100
    budget_fit_label: str
    cost_saving_tips: List[str] = []


# ─────────────────────────────────────────────
# Review / Sentiment Schemas
# ─────────────────────────────────────────────

class ReviewInsight(BaseModel):
    hotel_name: str
    total_reviews: int
    positive_pct: float
    negative_pct: float
    neutral_pct: float
    top_pros: List[str]
    top_cons: List[str]
    recurring_complaints: List[str]
    ai_summary: str
    sentiment_score: float


# ─────────────────────────────────────────────
# Itinerary Schemas
# ─────────────────────────────────────────────

class ItineraryDay(BaseModel):
    day_number: int
    date: Optional[str] = None
    title: str
    activities: List[str]
    meals: List[str]
    accommodation: str
    estimated_daily_cost_usd: float
    notes: Optional[str] = None


# ─────────────────────────────────────────────
# Full Trip Plan Result
# ─────────────────────────────────────────────

class TravelScore(BaseModel):
    total: float  # 0-100
    weather_score: float
    budget_score: float
    hotel_score: float
    sentiment_score: float
    flight_score: float
    label: str  # Excellent, Good, Fair, Poor
    explanation: str


class TripPlanResult(BaseModel):
    trip_id: int
    destination: str
    travel_score: TravelScore
    weather: WeatherResult
    recommended_hotels: List[HotelResult]
    flights: List[FlightResult]
    budget: BudgetBreakdown
    review_insights: List[ReviewInsight]
    itinerary: List[ItineraryDay]
    attractions: List[AttractionResult]
    nearby_services: List[NearbyService] = []
    personalized_tips: List[str]
    agent_reasoning: str
    city_rating: float = 0.0
    created_at: str


# ─────────────────────────────────────────────
# User Schemas
# ─────────────────────────────────────────────

class UserPreferences(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    preferred_climate: Optional[str] = None
    accommodation_type: Optional[str] = None
    travel_style: Optional[str] = None
    dietary: Optional[str] = None
    activities: Optional[List[str]] = None


class UserProfile(BaseModel):
    session_id: str
    name: Optional[str]
    persona: Optional[str]
    preferences: Optional[Dict[str, Any]]
    trip_count: int = 0
    created_at: str


# ─────────────────────────────────────────────
# Report Schemas
# ─────────────────────────────────────────────

class ReportGenerateRequest(BaseModel):
    trip_id: int
    session_id: str


class WhatsAppSendRequest(BaseModel):
    trip_id: int
    session_id: str
    phone_number: str = Field(..., description="Phone number in E.164 format, e.g. +14155552368")
    custom_message: Optional[str] = None


class ReportResponse(BaseModel):
    report_id: int
    trip_id: int
    pdf_filename: str
    pdf_path: str
    download_url: str
    created_at: str


# ─────────────────────────────────────────────
# Generic Response Schemas
# ─────────────────────────────────────────────

class SuccessResponse(BaseModel):
    success: bool = True
    message: str
    data: Optional[Any] = None


class ErrorResponse(BaseModel):
    success: bool = False
    error: str
    detail: Optional[str] = None
