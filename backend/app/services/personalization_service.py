"""
Personalization Service — travel persona classification and preference learning.
"""
import logging
from typing import Dict, Any, List, Optional
from app.schemas import TravelPersona

logger = logging.getLogger(__name__)

PERSONA_RULES = {
    TravelPersona.LUXURY: {
        "keywords": ["luxury", "5-star", "fine dining", "spa", "exclusive", "premium", "first class"],
        "budget_threshold": 5000,
        "description": "You seek premium experiences — top-tier hotels, gourmet restaurants, and exclusive access.",
        "icon": "👑",
    },
    TravelPersona.ADVENTURE: {
        "keywords": ["adventure", "hiking", "trekking", "diving", "skydiving", "camping", "extreme", "outdoor"],
        "description": "Thrills and natural landscapes define your ideal trip.",
        "icon": "🧗",
    },
    TravelPersona.CULTURAL: {
        "keywords": ["museum", "history", "art", "architecture", "heritage", "local culture", "culinary"],
        "description": "You travel to learn — museums, local customs, and historic sites are your priority.",
        "icon": "🎭",
    },
    TravelPersona.BUDGET: {
        "keywords": ["budget", "cheap", "affordable", "hostel", "backpacker", "frugal", "save"],
        "budget_threshold": 1500,
        "description": "You maximize experiences while minimizing spend — a strategic, savvy explorer.",
        "icon": "💰",
    },
    TravelPersona.RELAXATION: {
        "keywords": ["beach", "relax", "spa", "pool", "resort", "rest", "wellness", "yoga"],
        "description": "Rest and rejuvenation are your goals — beaches, spas, and serene environments.",
        "icon": "🏖️",
    },
    TravelPersona.FAMILY: {
        "keywords": ["family", "kids", "children", "theme park", "child-friendly", "educational"],
        "description": "Creating lasting memories with loved ones drives your travel decisions.",
        "icon": "👨‍👩‍👧‍👦",
    },
    TravelPersona.SOLO: {
        "keywords": ["solo", "alone", "independent", "self-discovery", "flexible", "freedom"],
        "description": "Freedom, flexibility, and self-discovery define your solo journeys.",
        "icon": "🎒",
    },
}


def classify_persona(
    preferences: Dict[str, Any],
    budget_usd: float = None,
    travel_purpose: str = None,
    trip_history: List[Dict] = None,
) -> TravelPersona:
    """Classify user travel persona based on preferences and behavior."""
    scores = {persona: 0 for persona in TravelPersona}

    # Check keywords in preferences and purpose
    text_to_scan = " ".join([
        str(preferences.get("travel_style", "")),
        str(preferences.get("activities", "")),
        str(preferences.get("accommodation_type", "")),
        str(travel_purpose or ""),
    ]).lower()

    for persona, rules in PERSONA_RULES.items():
        for kw in rules["keywords"]:
            if kw in text_to_scan:
                scores[persona] += 2

    # Budget-based scoring
    if budget_usd:
        if budget_usd >= 5000:
            scores[TravelPersona.LUXURY] += 3
        elif budget_usd <= 1500:
            scores[TravelPersona.BUDGET] += 3

    # Number of travelers
    if preferences.get("travelers_count", 1) >= 3:
        scores[TravelPersona.FAMILY] += 2

    # Default to Cultural if tied or no clear winner
    best = max(scores, key=scores.get)
    if scores[best] == 0:
        return TravelPersona.CULTURAL

    return best


def get_persona_info(persona: TravelPersona) -> Dict[str, str]:
    """Get display info for a travel persona."""
    rules = PERSONA_RULES.get(persona, {})
    return {
        "name": persona.value,
        "icon": rules.get("icon", "✈️"),
        "description": rules.get("description", "Passionate traveler with unique preferences."),
    }


def generate_personalized_tips(
    persona: TravelPersona,
    destination: str,
    budget_usd: float = None,
    trip_count: int = 0,
) -> List[str]:
    """Generate personalized travel suggestions based on user persona."""
    tips = {
        TravelPersona.LUXURY: [
            f"Consider booking a private guided tour of {destination}'s top landmarks",
            "Request late checkout and room upgrades at your hotel — loyalty status helps",
            "Reserve restaurant tables at least 2 weeks in advance for Michelin-star dining",
            "Look into private airport transfers for a seamless start to your trip",
        ],
        TravelPersona.ADVENTURE: [
            f"Check local outdoor activity operators in {destination} — book guided excursions early",
            "Pack a versatile daypack and sturdy footwear for spontaneous hikes",
            "Look for adventure hostels — great for meeting like-minded travelers",
            "Research permit requirements for national parks in advance",
        ],
        TravelPersona.CULTURAL: [
            f"Visit {destination}'s local markets on weekday mornings to avoid crowds",
            "Download a local audio tour app for self-guided museum exploration",
            "Take a hands-on cooking class to learn local culinary traditions",
            "Attend a free local festival or cultural event — check city event calendars",
        ],
        TravelPersona.BUDGET: [
            "Book accommodations at least 6 weeks ahead for best rates",
            f"Use public transit in {destination} — it's often excellent and very cheap",
            "Eat where the locals eat — avoid tourist-trap restaurants near landmarks",
            "Look for city tourist passes — they bundle attractions at 30-50% savings",
        ],
        TravelPersona.RELAXATION: [
            f"Book a beachfront property in {destination} for the best sunrise views",
            "Schedule spa treatments during off-peak hours (10 AM–2 PM) for availability",
            "Consider all-inclusive resorts to minimize decision fatigue",
            "Pack noise-cancelling headphones and a good book for downtime",
        ],
        TravelPersona.FAMILY: [
            f"Research family-friendly neighborhoods in {destination} for your base",
            "Look for hotels offering complimentary kids' meals and family suites",
            "Book activity tickets online to skip queues at popular attractions",
            "Pack a small first-aid kit and children's travel essentials",
        ],
        TravelPersona.SOLO: [
            f"Join a group day tour in {destination} to meet fellow travelers",
            "Stay in a social hostel with common areas — great for making connections",
            "Share your daily itinerary with a friend or family member back home",
            "Download offline maps — you'll rely on them more than you expect",
        ],
    }

    persona_tips = tips.get(persona, tips[TravelPersona.CULTURAL])

    # Add returning traveler tip
    if trip_count >= 2:
        persona_tips.append(
            f"As an experienced traveler, try venturing beyond tourist hotspots in {destination} for authentic local experiences."
        )

    return persona_tips
