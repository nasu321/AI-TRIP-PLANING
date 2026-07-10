"""
Flight Service — Uses real OpenFlights database + IATA price index.

Data sources:
  - OpenFlights routes.dat  (GitHub: jpatokal/openflights, ODbL license)
  - OpenFlights airports.dat (same source)
  - IATA flight_price_index.csv (derived from IATA Economics 2024)

Falls back to realistic model if destination not in database.
"""
import random
import logging
from typing import List, Optional
from app.config import settings
from app.schemas import FlightResult
from app.services.data_manager import data_manager, detect_region

logger = logging.getLogger(__name__)


def calculate_affordability_score(price: float, budget: float) -> float:
    if not budget:
        return 70.0
    flight_pct = price / budget
    if flight_pct <= 0.20: return 95.0
    elif flight_pct <= 0.30: return 80.0
    elif flight_pct <= 0.40: return 65.0
    elif flight_pct <= 0.55: return 45.0
    else: return max(10, (1 - flight_pct) * 100)


async def get_flights(
    origin: str = "New York",
    destination: str = "Paris",
    start_date: str = None,
    budget_usd: float = None,
    origin_region: str = None,
) -> List[FlightResult]:
    """Get flight options, using real OpenFlights + IATA price data."""
    # Ensure datasets are loaded
    data_manager.load()

    if not origin_region:
        origin_region = detect_region(origin) if origin != "User's Origin" else "Europe"

    # Get real price data from IATA index
    price_data = data_manager.get_flight_prices(destination, origin_region)
    # Get real airport info
    airports = data_manager.find_airports(destination, limit=1)
    # Get real airlines from OpenFlights routes
    real_airlines = data_manager.get_airlines_serving(destination)

    iata_code = airports[0]["iata"] if airports else "INT"
    dest_city  = airports[0]["city"] if airports else destination.split(",")[0].strip()

    avg_price  = price_data["avg_roundtrip_usd"]
    min_price  = price_data["min_price_usd"]
    avg_dur    = price_data["avg_duration_hours"]
    db_airlines = price_data.get("airlines", [])
    is_from_db = price_data.get("data_from_db", False)

    # Use real airline names from routes DB if available, else from price index
    airline_pool = real_airlines if real_airlines else db_airlines
    if not airline_pool:
        airline_pool = ["Emirates", "Lufthansa", "Air France", "Singapore Airlines",
                        "Turkish Airlines", "British Airways", "KLM", "Qatar Airways"]

    random.seed(hash(f"{origin}{destination}") % 10000)
    flights = []

    # Build 4-5 realistic options around the real price point
    scenarios = [
        {"stops": 0, "price_mult": 1.15, "dur_mult": 1.0,  "label": "Direct"},
        {"stops": 0, "price_mult": 1.05, "dur_mult": 1.0,  "label": "Direct"},
        {"stops": 1, "price_mult": 0.82, "dur_mult": 1.25, "label": "1 Stop"},
        {"stops": 1, "price_mult": 0.75, "dur_mult": 1.30, "label": "Budget 1-Stop"},
        {"stops": 2, "price_mult": 0.62, "dur_mult": 1.55, "label": "2 Stops"},
    ]

    for i, sc in enumerate(scenarios[:4]):
        airline = airline_pool[i % len(airline_pool)] if airline_pool else "International Airlines"
        # Shorten airline name if needed
        airline_short = airline[:30] if len(airline) > 30 else airline
        price = round(avg_price * sc["price_mult"] * random.uniform(0.92, 1.08), 0)
        price = max(min_price * 0.85, price)  # don't go below near-min
        duration = round(avg_dur * sc["dur_mult"] + random.uniform(-0.5, 0.5), 1)
        dep_hour = random.choice([6, 8, 10, 14, 18, 21])
        dep_min  = random.choice([0, 15, 30, 45])
        arr_hour = (dep_hour + int(duration)) % 24
        arr_min = (dep_min + int((duration % 1) * 60)) % 60

        source_tag = "📊 DB" if is_from_db else "📈 Est."
        dest_label = f"{dest_city} ({iata_code})"

        flights.append(FlightResult(
            airline=f"{airline_short}  {source_tag}",
            flight_number=f"{airline_short[:2].upper().replace(' ','')}{random.randint(100,999)}",
            origin=f"{origin}",
            destination=dest_label,
            price_usd=price,
            duration_hours=duration,
            departure_time=f"{dep_hour:02d}:{dep_min:02d}",
            arrival_time=f"{arr_hour:02d}:{arr_min:02d}",
            stops=sc["stops"],
            is_cheapest=False,
            affordability_score=calculate_affordability_score(price, budget_usd),
        ))

    # Mark cheapest
    flights.sort(key=lambda f: f.price_usd)
    flights[0] = flights[0].model_copy(update={"is_cheapest": True})

    # Mark fastest
    flights.sort(key=lambda f: f.duration_hours)
    flights[0] = flights[0].model_copy(update={"is_fastest": True})
    
    # Restore sorting by price by default
    flights.sort(key=lambda f: f.price_usd)

    source_info = f"OpenFlights DB + IATA 2024" if is_from_db else "Estimated from route model"
    logger.info(
        f"[FlightService] {len(flights)} flights to {dest_city} ({iata_code}) "
        f"| Base: ${avg_price:.0f} | Airlines from DB: {len(real_airlines)} | Source: {source_info}"
    )
    return flights
