"""
Weather Service — OpenWeatherMap API with rich mock fallback.
Returns 7-day forecast, suitability scoring, and packing tips.
"""
import httpx
import random
import logging
from typing import Dict, Any, List
from app.config import settings
from app.schemas import WeatherResult, WeatherDay

logger = logging.getLogger(__name__)

# Destination-based mock climate profiles
MOCK_CLIMATE_PROFILES = {
    "tropical": {
        "conditions": ["Sunny", "Partly Cloudy", "Tropical Showers", "Humid & Warm"],
        "temp_range": (26, 34),
        "humidity": (70, 90),
        "precip": (0, 15),
    },
    "mediterranean": {
        "conditions": ["Sunny", "Clear", "Warm & Breezy", "Partly Cloudy"],
        "temp_range": (20, 30),
        "humidity": (40, 65),
        "precip": (0, 5),
    },
    "temperate": {
        "conditions": ["Cloudy", "Mild", "Light Rain", "Overcast", "Partly Sunny"],
        "temp_range": (10, 22),
        "humidity": (55, 75),
        "precip": (2, 10),
    },
    "cold": {
        "conditions": ["Cold & Cloudy", "Snowy", "Frigid", "Overcast", "Light Snow"],
        "temp_range": (-5, 8),
        "humidity": (60, 80),
        "precip": (0, 8),
    },
    "desert": {
        "conditions": ["Very Hot & Sunny", "Scorching", "Dry & Clear", "Hot & Windy"],
        "temp_range": (32, 44),
        "humidity": (10, 25),
        "precip": (0, 1),
    },
}

DESTINATION_CLIMATES = {
    "paris": "temperate", "london": "temperate", "berlin": "temperate",
    "tokyo": "temperate", "new york": "temperate", "chicago": "temperate",
    "rome": "mediterranean", "barcelona": "mediterranean", "athens": "mediterranean",
    "lisbon": "mediterranean", "madrid": "mediterranean",
    "bali": "tropical", "bangkok": "tropical", "singapore": "tropical",
    "miami": "tropical", "cancun": "tropical", "maldives": "tropical",
    "dubai": "desert", "riyadh": "desert", "las vegas": "desert",
    "reykjavik": "cold", "oslo": "cold", "zurich": "cold",
}

WEATHER_ICONS = {
    "Sunny": "☀️", "Clear": "🌤️", "Partly Cloudy": "⛅", "Cloudy": "☁️",
    "Light Rain": "🌦️", "Tropical Showers": "🌧️", "Overcast": "🌥️",
    "Mild": "🌤️", "Warm & Breezy": "🌬️", "Snowy": "❄️",
    "Very Hot & Sunny": "🔆", "Scorching": "🌡️", "Humid & Warm": "💧",
    "Cold & Cloudy": "🌨️", "Frigid": "🥶", "Light Snow": "🌨️",
    "Hot & Windy": "🌵", "Dry & Clear": "☀️", "Partly Sunny": "🌤️",
}


def get_climate_profile(destination: str) -> Dict:
    """Match destination to a climate profile."""
    dest_lower = destination.lower()
    for key, profile in DESTINATION_CLIMATES.items():
        if key in dest_lower:
            return MOCK_CLIMATE_PROFILES[profile]
    return MOCK_CLIMATE_PROFILES["temperate"]  # default


def calculate_suitability_score(forecast: List[WeatherDay]) -> float:
    """Calculate weather suitability score 0-100."""
    scores = []
    for day in forecast:
        score = 70
        # Temperature comfort
        if 18 <= day.temp_high_c <= 28:
            score += 20
        elif 10 <= day.temp_high_c <= 35:
            score += 10
        else:
            score -= 10
        # Rain penalty
        if day.precipitation_mm > 10:
            score -= 15
        elif day.precipitation_mm > 5:
            score -= 7
        # Humidity penalty
        if day.humidity_pct > 85:
            score -= 10
        scores.append(min(max(score, 0), 100))
    return round(sum(scores) / len(scores), 1) if scores else 70.0


def get_packing_tips(profile_name: str, suitability: float) -> List[str]:
    """Return context-aware packing tips."""
    tips_map = {
        "tropical": [
            "🕶️ Sunglasses and high-SPF sunscreen are essential",
            "👗 Pack light, breathable fabrics (linen, cotton)",
            "☂️ Bring a compact umbrella for sudden showers",
            "💧 Stay hydrated — carry a water bottle",
            "🦟 Pack insect repellent for outdoor excursions",
        ],
        "mediterranean": [
            "🧴 Sunscreen SPF 50+ for midday sun",
            "👡 Comfortable walking shoes for cobblestone streets",
            "🧣 A light scarf/shawl for visiting churches",
            "💳 Mix of cash and cards — some villages prefer cash",
            "📷 Your camera will be constantly in use!",
        ],
        "temperate": [
            "🧥 Layer up — mornings and evenings can be cool",
            "☂️ Compact waterproof jacket is a must",
            "👟 Comfortable walking shoes — you'll explore a lot",
            "🌡️ Check daily forecasts and dress accordingly",
            "🎒 A daypack works well for city exploration",
        ],
        "cold": [
            "🧤 Thermal underwear and insulated gloves essential",
            "🥾 Waterproof, insulated boots for snow and ice",
            "🧣 Scarf, hat, and heavy coat are non-negotiable",
            "🔋 Cold drains phone batteries faster — bring a power bank",
            "🛁 Moisturizer — cold air dries skin quickly",
        ],
        "desert": [
            "🌞 Loose, light-colored long-sleeved clothing to reflect heat",
            "💧 Carry at least 2L of water per person daily",
            "🧴 Very high SPF sunscreen, reapply every 2 hours",
            "🕶️ UV-protective sunglasses and a wide-brim hat",
            "🌙 Evenings can be surprisingly cool — bring a light layer",
        ],
    }
    # Detect profile from suitability context
    for key in tips_map:
        return tips_map.get(key, tips_map["temperate"])
    return tips_map["temperate"]


async def get_weather(destination: str, start_date: str = None) -> WeatherResult:
    """
    Fetch weather forecast for destination.
    Falls back to realistic mock data if API key not configured.
    """
    if not settings.USE_MOCK_WEATHER and settings.WEATHER_API_KEY:
        return await _fetch_real_weather(destination)
    else:
        return _generate_mock_weather(destination, start_date)


async def _fetch_real_weather(destination: str) -> WeatherResult:
    """Fetch real weather data from OpenWeatherMap API."""
    try:
        async with httpx.AsyncClient() as client:
            # Get coordinates
            geo_response = await client.get(
                f"{settings.WEATHER_BASE_URL}/weather",
                params={"q": destination, "appid": settings.WEATHER_API_KEY, "units": "metric"},
                timeout=10,
            )
            geo_data = geo_response.json()
            lat = geo_data["coord"]["lat"]
            lon = geo_data["coord"]["lon"]

            # Get 7-day forecast
            forecast_response = await client.get(
                f"{settings.WEATHER_BASE_URL}/forecast",
                params={
                    "lat": lat, "lon": lon,
                    "appid": settings.WEATHER_API_KEY,
                    "units": "metric", "cnt": 7
                },
                timeout=10,
            )
            forecast_data = forecast_response.json()

            forecast_days = []
            for i, item in enumerate(forecast_data["list"][:7]):
                condition = item["weather"][0]["description"].title()
                forecast_days.append(WeatherDay(
                    date=f"Day {i+1}",
                    condition=condition,
                    temp_high_c=round(item["main"]["temp_max"], 1),
                    temp_low_c=round(item["main"]["temp_min"], 1),
                    humidity_pct=item["main"]["humidity"],
                    precipitation_mm=item.get("rain", {}).get("3h", 0),
                    wind_kmh=round(item["wind"]["speed"] * 3.6, 1),
                    icon=WEATHER_ICONS.get(condition, "🌤️"),
                ))

            score = calculate_suitability_score(forecast_days)
            return WeatherResult(
                destination=destination,
                forecast=forecast_days,
                suitability_score=score,
                suitability_label=_score_label(score),
                packing_tips=get_packing_tips("temperate", score),
                best_time_note=f"Weather analysis for {destination} shows {'favorable' if score > 70 else 'moderate'} conditions.",
            )
    except Exception as e:
        logger.warning(f"Real weather API failed: {e}. Falling back to mock.")
        return _generate_mock_weather(destination)


def _generate_mock_weather(destination: str, start_date: str = None) -> WeatherResult:
    """Generate realistic mock weather data."""
    profile = get_climate_profile(destination)
    random.seed(hash(destination) % 1000)

    # Determine profile name
    dest_lower = destination.lower()
    profile_name = "temperate"
    for key, pname in DESTINATION_CLIMATES.items():
        if key in dest_lower:
            profile_name = pname
            break

    forecast = []
    days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    for i in range(7):
        condition = random.choice(profile["conditions"])
        t_low, t_high = profile["temp_range"]
        forecast.append(WeatherDay(
            date=days[i % 7],
            condition=condition,
            temp_high_c=round(random.uniform(t_low + 3, t_high), 1),
            temp_low_c=round(random.uniform(t_low, t_high - 5), 1),
            humidity_pct=random.randint(*profile["humidity"]),
            precipitation_mm=round(random.uniform(*profile["precip"]), 1),
            wind_kmh=round(random.uniform(5, 30), 1),
            icon=WEATHER_ICONS.get(condition, "🌤️"),
        ))

    score = calculate_suitability_score(forecast)
    tips = get_packing_tips(profile_name, score)

    best_time_notes = {
        "tropical": f"Best time to visit {destination} is during the dry season (Nov–Apr). Expect warm, humid days.",
        "mediterranean": f"{destination} is delightful in spring and fall. Summer is peak season — book hotels early.",
        "temperate": f"{destination} is pleasant in summer. Spring offers lush scenery and fewer crowds.",
        "cold": f"Pack heavy winter gear for {destination}. Winter may offer Northern Lights opportunities.",
        "desert": f"Visit {destination} in winter months (Oct–Feb) to avoid extreme heat.",
    }

    return WeatherResult(
        destination=destination,
        forecast=forecast,
        suitability_score=score,
        suitability_label=_score_label(score),
        packing_tips=tips,
        best_time_note=best_time_notes.get(profile_name, f"Weather in {destination} varies seasonally."),
    )


def _score_label(score: float) -> str:
    if score >= 85:
        return "Excellent ✅"
    elif score >= 70:
        return "Good 👍"
    elif score >= 55:
        return "Fair ⚠️"
    else:
        return "Challenging 🌧️"
