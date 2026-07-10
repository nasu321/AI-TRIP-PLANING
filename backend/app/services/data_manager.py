"""
Data Manager — loads and queries all open datasets.

Datasets loaded:
  - OpenFlights airports.dat  (GitHub: jpatokal/openflights, ODbL)
  - OpenFlights routes.dat    (GitHub: jpatokal/openflights, ODbL)
  - OpenFlights airlines.dat  (GitHub: jpatokal/openflights, ODbL)
  - international_hotel_prices.csv (Numbeo/STR Global/Booking.com 2024)
  - cost_of_living.csv        (Numbeo Cost of Living Index 2024)
  - flight_price_index.csv    (IATA Economics / Rome2Rio 2024)
  - country_codes.csv         (OKFN datasets, CC0)
"""
import math
import logging
import pandas as pd
from pathlib import Path
from typing import Optional, Dict, Any, List
from functools import lru_cache

logger = logging.getLogger(__name__)

DATA_DIR = Path(__file__).parent.parent / "data"


# ─────────────────────────────────────────────────────────────
# Region detection
# ─────────────────────────────────────────────────────────────
CITY_REGION_MAP = {
    "north america": ["new york","los angeles","miami","las vegas","toronto","vancouver",
                      "chicago","san francisco","mexico city","cancun"],
    "europe":        ["paris","london","rome","barcelona","amsterdam","berlin","madrid",
                      "lisbon","vienna","prague","athens","zurich","istanbul","reykjavik",
                      "oslo","stockholm","copenhagen","helsinki","santorini"],
    "asia":          ["tokyo","bali","bangkok","singapore","kuala lumpur","seoul","beijing",
                      "shanghai","hong kong","phuket","ho chi minh","hanoi","siem reap",
                      "manila","yangon","taipei","kyoto","osaka","colombo","kathmandu",
                      "maldives","delhi","mumbai","goa"],
    "middle east":   ["dubai","abu dhabi","doha","riyadh","muscat","cairo","marrakech","amman"],
    "australia":     ["sydney","melbourne","brisbane","perth","auckland"],
    "south america": ["rio de janeiro","buenos aires","lima","bogota","santiago"],
    "africa":        ["nairobi","cape town","zanzibar","accra","lagos","johannesburg"],
}

def detect_region(destination: str) -> str:
    dest_l = destination.lower()
    for region, cities in CITY_REGION_MAP.items():
        for city in cities:
            if city in dest_l:
                return region.title()
    # Country-based fallback
    europe_kw = ["france","uk","germany","italy","spain","portugal","netherlands",
                 "austria","czech","greece","turkey","switzerland","sweden","norway",
                 "denmark","finland","iceland","poland"]
    asia_kw   = ["japan","indonesia","thailand","malaysia","vietnam","cambodia",
                 "india","china","korea","taiwan","philippines","myanmar","sri lanka","nepal"]
    for kw in europe_kw:
        if kw in dest_l: return "Europe"
    for kw in asia_kw:
        if kw in dest_l: return "Asia"
    if any(x in dest_l for x in ["usa","united states","canada","mexico"]): return "North America"
    if any(x in dest_l for x in ["uae","dubai","qatar","saudi","egypt","morocco"]): return "Middle East"
    if any(x in dest_l for x in ["australia","zealand"]): return "Australia"
    if any(x in dest_l for x in ["brazil","argentina","peru","colombia","chile"]): return "South America"
    if any(x in dest_l for x in ["kenya","south africa","nigeria","ghana","tanzania"]): return "Africa"
    return "Europe"  # default


class DataManager:
    """Central data manager. Call load() once at startup."""

    def __init__(self):
        self._airports: Optional[pd.DataFrame]      = None
        self._routes:   Optional[pd.DataFrame]      = None
        self._airlines: Optional[pd.DataFrame]      = None
        self._hotels:   Optional[pd.DataFrame]      = None
        self._budget:   Optional[pd.DataFrame]      = None
        self._flights:  Optional[pd.DataFrame]      = None
        self._places:   Optional[pd.DataFrame]      = None
        self._loaded = False

    def load(self):
        if self._loaded:
            return
        logger.info("[DataManager] Loading datasets from disk...")
        try:
            self._airports = pd.read_csv(
                DATA_DIR / "airports.dat", header=None, encoding="utf-8", on_bad_lines="skip",
                names=["id","name","city","country","iata","icao","lat","lon","alt","tz","dst","tz_db","type","source"]
            )
            self._airports = self._airports[self._airports["iata"].notna() & (self._airports["iata"] != r"\N")]
            logger.info(f"[DataManager] Airports: {len(self._airports):,} records")
        except Exception as e:
            logger.warning(f"[DataManager] Airports load failed: {e}")

        try:
            self._routes = pd.read_csv(
                DATA_DIR / "routes.dat", header=None, encoding="utf-8", on_bad_lines="skip",
                names=["airline","airline_id","src","src_id","dst","dst_id","codeshare","stops","equipment"]
            )
            logger.info(f"[DataManager] Routes: {len(self._routes):,} records")
        except Exception as e:
            logger.warning(f"[DataManager] Routes load failed: {e}")

        try:
            self._airlines = pd.read_csv(
                DATA_DIR / "airlines.dat", header=None, encoding="utf-8", on_bad_lines="skip",
                names=["id","name","alias","iata","icao","callsign","country","active"]
            )
            self._airlines = self._airlines[self._airlines["active"] == "Y"]
            logger.info(f"[DataManager] Airlines: {len(self._airlines):,} active")
        except Exception as e:
            logger.warning(f"[DataManager] Airlines load failed: {e}")

        try:
            self._hotels = pd.read_csv(DATA_DIR / "international_hotel_prices.csv", encoding="utf-8")
            self._hotels["city_lower"] = self._hotels["city"].str.lower()
            self._hotels["budget_hotel_usd"] = pd.to_numeric(self._hotels["budget_hotel_usd"])
            self._hotels["mid_hotel_usd"]    = pd.to_numeric(self._hotels["mid_hotel_usd"])
            self._hotels["luxury_hotel_usd"] = pd.to_numeric(self._hotels["luxury_hotel_usd"])
            logger.info(f"[DataManager] Hotel prices: {len(self._hotels):,} cities")
        except Exception as e:
            logger.warning(f"[DataManager] Hotel prices load failed: {e}")

        try:
            self._budget = pd.read_csv(DATA_DIR / "cost_of_living.csv", encoding="utf-8")
            self._budget["city_lower"] = self._budget["city"].str.lower()
            for col in ["daily_backpacker","daily_mid","daily_luxury","meal_cheap",
                        "meal_mid","meal_fine","local_transport_day","attraction_avg","numbeo_index"]:
                self._budget[col] = pd.to_numeric(self._budget[col])
            logger.info(f"[DataManager] Cost of living: {len(self._budget):,} cities")
        except Exception as e:
            logger.warning(f"[DataManager] Budget load failed: {e}")

        try:
            self._flights = pd.read_csv(DATA_DIR / "flight_price_index.csv", encoding="utf-8")
            self._flights["destination_city_lower"] = self._flights["destination_city"].str.lower()
            self._flights["avg_roundtrip_usd"] = pd.to_numeric(self._flights["avg_roundtrip_usd"])
            self._flights["min_price_usd"]     = pd.to_numeric(self._flights["min_price_usd"])
            self._flights["avg_duration_hours"] = pd.to_numeric(self._flights["avg_duration_hours"])
            logger.info(f"[DataManager] Flight price index: {len(self._flights):,} routes")
        except Exception as e:
            logger.warning(f"[DataManager] Flight price index load failed: {e}")

        try:
            self._places = pd.read_csv(DATA_DIR / "international_places.csv", encoding="utf-8")
            self._places["city_lower"] = self._places["city"].str.lower()
            self._places["country_lower"] = self._places["country"].str.lower()
            logger.info(f"[DataManager] Places: {len(self._places):,} attractions")
        except Exception as e:
            logger.warning(f"[DataManager] Places load failed: {e}")

        self._loaded = True
        logger.info("[DataManager] ✅ All datasets loaded.")

    # ─────────────────────────────────────────────────────────
    # Dataset stats (for UI display)
    # ─────────────────────────────────────────────────────────
    def get_stats(self) -> Dict[str, Any]:
        return {
            "airports":  len(self._airports) if self._airports is not None else 0,
            "routes":    len(self._routes)   if self._routes   is not None else 0,
            "airlines":  len(self._airlines) if self._airlines is not None else 0,
            "hotel_cities": len(self._hotels) if self._hotels  is not None else 0,
            "budget_cities": len(self._budget) if self._budget is not None else 0,
            "flight_routes": len(self._flights) if self._flights is not None else 0,
            "places":    len(self._places)   if self._places   is not None else 0,
        }

    def get_registry(self) -> List[Dict]:
        import json
        try:
            with open(DATA_DIR / "registry.json", encoding="utf-8") as f:
                return json.load(f)["datasets"]
        except Exception:
            return []

    # ─────────────────────────────────────────────────────────
    # Hotel Prices
    # ─────────────────────────────────────────────────────────
    def get_hotel_prices(self, destination: str) -> Dict[str, Any]:
        """Return hotel price tiers for a destination."""
        if self._hotels is None:
            return self._default_hotel_prices(destination)

        dest_l = destination.lower().split(",")[0].strip()
        # Exact city match
        match = self._hotels[self._hotels["city_lower"] == dest_l]
        if match.empty:
            # Partial match
            match = self._hotels[self._hotels["city_lower"].str.contains(dest_l[:6], na=False)]
        if match.empty:
            return self._default_hotel_prices(destination)

        row = match.iloc[0]
        return {
            "city":          row["city"],
            "country":       row["country"],
            "budget_usd":    float(row["budget_hotel_usd"]),
            "mid_usd":       float(row["mid_hotel_usd"]),
            "luxury_usd":    float(row["luxury_hotel_usd"]),
            "avg_rating":    float(row["avg_rating"]),
            "demand_index":  float(row["demand_index"]),
            "source":        str(row["source"]),
            "data_from_db":  True,
        }

    def _default_hotel_prices(self, destination: str) -> Dict[str, Any]:
        return {"budget_usd":80,"mid_usd":160,"luxury_usd":380,"avg_rating":4.2,
                "demand_index":80,"source":"Default estimate","data_from_db":False}

    # ─────────────────────────────────────────────────────────
    # Cost of Living / Budget
    # ─────────────────────────────────────────────────────────
    def get_cost_of_living(self, destination: str) -> Dict[str, Any]:
        """Return daily cost tiers for a destination."""
        if self._budget is None:
            return self._default_cost()

        dest_l = destination.lower().split(",")[0].strip()
        match = self._budget[self._budget["city_lower"] == dest_l]
        if match.empty:
            match = self._budget[self._budget["city_lower"].str.contains(dest_l[:6], na=False)]
        if match.empty:
            return self._default_cost()

        row = match.iloc[0]
        return {
            "city":                 row["city"],
            "country":              row["country"],
            "daily_backpacker":     float(row["daily_backpacker"]),
            "daily_mid":            float(row["daily_mid"]),
            "daily_luxury":         float(row["daily_luxury"]),
            "meal_cheap":           float(row["meal_cheap"]),
            "meal_mid":             float(row["meal_mid"]),
            "meal_fine":            float(row["meal_fine"]),
            "local_transport_day":  float(row["local_transport_day"]),
            "attraction_avg":       float(row["attraction_avg"]),
            "numbeo_index":         float(row["numbeo_index"]),
            "source":               str(row["source"]),
            "data_from_db":         True,
        }

    def _default_cost(self) -> Dict[str, Any]:
        return {"daily_backpacker":40,"daily_mid":100,"daily_luxury":280,"meal_cheap":8,
                "meal_mid":20,"meal_fine":60,"local_transport_day":8,"attraction_avg":15,
                "numbeo_index":60,"source":"Default estimate","data_from_db":False}

    # ─────────────────────────────────────────────────────────
    # Flight Prices
    # ─────────────────────────────────────────────────────────
    def get_flight_prices(self, destination: str, origin_region: str = "Europe") -> Dict[str, Any]:
        """Return avg flight prices to destination from given region."""
        if self._flights is None:
            return self._default_flight(destination)

        dest_l = destination.lower().split(",")[0].strip()
        region_l = origin_region.lower()

        # Match by destination city + region
        match = self._flights[
            self._flights["destination_city_lower"].str.contains(dest_l[:6], na=False) &
            self._flights["origin_region"].str.lower().str.contains(region_l.split()[0], na=False)
        ]

        if match.empty:
            # Any region matching this destination
            match = self._flights[self._flights["destination_city_lower"].str.contains(dest_l[:6], na=False)]

        if match.empty:
            return self._default_flight(destination)

        row = match.iloc[0]
        return {
            "destination_city":    row["destination_city"],
            "destination_country": row["destination_country"],
            "destination_iata":    row["destination_iata"],
            "avg_roundtrip_usd":   float(row["avg_roundtrip_usd"]),
            "min_price_usd":       float(row["min_price_usd"]),
            "avg_duration_hours":  float(row["avg_duration_hours"]),
            "airlines":            str(row["airlines"]).split(","),
            "origin_region":       str(row["origin_region"]),
            "source":              str(row["source"]),
            "data_from_db":        True,
        }

    def _default_flight(self, destination: str) -> Dict[str, Any]:
        return {"avg_roundtrip_usd":600,"min_price_usd":350,"avg_duration_hours":10,
                "airlines":["Various Airlines"],"source":"Default estimate","data_from_db":False}

    # ─────────────────────────────────────────────────────────
    # OpenFlights: Airport lookup
    # ─────────────────────────────────────────────────────────
    def find_airports(self, destination: str, limit: int = 5) -> List[Dict]:
        """Find airport records for destination city/country."""
        if self._airports is None:
            return []
        dest_l = destination.lower().split(",")[0].strip()
        match = self._airports[
            self._airports["city"].str.lower().str.contains(dest_l[:8], na=False) |
            self._airports["country"].str.lower().str.contains(dest_l[:8], na=False)
        ].head(limit)
        rows = match[["name","city","country","iata","lat","lon"]].copy()
        # Replace NaN with None for JSON safety
        rows = rows.where(rows.notna(), other=None)
        return rows.to_dict("records")

    # ─────────────────────────────────────────────────────────
    # OpenFlights: Real routes for destination airport
    # ─────────────────────────────────────────────────────────
    def get_routes_to(self, destination: str, limit: int = 20) -> List[Dict]:
        """Get real airline routes arriving at destination."""
        if self._routes is None or self._airports is None:
            return []
        airports = self.find_airports(destination, limit=3)
        if not airports:
            return []
        iata_codes = [a["iata"] for a in airports if a.get("iata") and a["iata"] != r"\N"]
        if not iata_codes:
            return []
        routes = self._routes[self._routes["dst"].isin(iata_codes)].head(limit)
        rows = routes[["airline","src","dst","stops","codeshare"]].copy()
        rows = rows.where(rows.notna(), other=None)
        return rows.to_dict("records")

    def get_airlines_serving(self, destination: str) -> List[str]:
        """Return list of real airline codes serving destination."""
        routes = self.get_routes_to(destination, limit=50)
        codes = list(set([r["airline"] for r in routes if r.get("airline") and r["airline"] != r"\N"]))
        # Resolve names from airlines df
        names = []
        if self._airlines is not None:
            for code in codes[:10]:
                match = self._airlines[self._airlines["iata"] == code]
                if not match.empty:
                    names.append(match.iloc[0]["name"])
        return names[:8] if names else codes[:8]

    # ─────────────────────────────────────────────────────────
    # Tourist Places / Attractions
    # ─────────────────────────────────────────────────────────
    def get_attractions(self, destination: str) -> List[Dict]:
        """Return list of attractions for destination from international_places.csv"""
        if getattr(self, "_places", None) is None:
            return []
        
        dest_l = destination.lower().split(",")[0].strip()
        match = self._places[
            self._places["city_lower"].str.contains(dest_l[:8], na=False) |
            self._places["country_lower"].str.contains(dest_l[:8], na=False)
        ]
        
        if match.empty:
            return []
            
        rows = match.copy()
        rows = rows.where(rows.notna(), other=None)
        
        # Format the linked flight data gracefully
        result = []
        for r in rows.to_dict("records"):
            # Include basic place data
            item = r.copy()
            # Rename for frontend consistency if needed
            if "nearest_airport_iata" in item and item["nearest_airport_iata"]:
                item["description"] = f"{item['description']} (Nearest Airport: {item['nearest_airport_iata']})"
            result.append(item)
            
        return result

    # ─────────────────────────────────────────────────────────
    # All cities (for autocomplete / explorer)
    # ─────────────────────────────────────────────────────────
    def get_all_hotel_cities(self) -> pd.DataFrame:
        return self._hotels if self._hotels is not None else pd.DataFrame()

    def get_all_budget_cities(self) -> pd.DataFrame:
        return self._budget if self._budget is not None else pd.DataFrame()

    def get_all_flight_routes(self) -> pd.DataFrame:
        return self._flights if self._flights is not None else pd.DataFrame()


# ── Global Singleton ──────────────────────────────────────────
data_manager = DataManager()
