"""
Link the Flight Ticket Database with the International Trip Places Database.
This script adds the nearest airport (IATA) and average flight cost to each tourist place.
"""
import sys, math
import pandas as pd
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

DATA_DIR = Path("C:/datascience/cylsiss/backend/app/data")

def haversine(lat1, lon1, lat2, lon2):
    """Calculate the great circle distance in kilometers between two points on the earth."""
    # Convert decimal degrees to radians 
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    # Haversine formula 
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a)) 
    r = 6371 # Radius of earth in kilometers.
    return c * r

print("Loading databases...")
places = pd.read_csv(DATA_DIR / "international_places.csv", encoding="utf-8")
airports = pd.read_csv(DATA_DIR / "airports.dat", header=None, encoding="utf-8", on_bad_lines="skip",
                        names=["id","name","city","country","iata","icao","lat","lon","alt","tz","dst","tz_db","type","source"])
airports = airports[airports["iata"].notna() & (airports["iata"] != "\\N") & (airports["type"] == "airport")]

flights = pd.read_csv(DATA_DIR / "flight_price_index.csv", encoding="utf-8")

# Prepare new columns
nearest_iata = []
nearest_airport_name = []
flight_cost = []

print("Linking places with airports and flight prices...")
for idx, row in places.iterrows():
    p_lat = float(row["lat"])
    p_lon = float(row["lon"])
    
    # Filter airports in the same country to speed up
    country_airports = airports[airports["country"].str.lower() == str(row["country"]).lower()].copy()
    if country_airports.empty:
        # Fallback to all airports if country name mismatches (e.g., USA vs United States)
        country_airports = airports.copy()
        
    country_airports["dist"] = country_airports.apply(lambda r: haversine(p_lat, p_lon, r["lat"], r["lon"]), axis=1)
    
    closest = country_airports.loc[country_airports["dist"].idxmin()] if not country_airports.empty else None
    
    if closest is not None:
        iata = closest["iata"]
        name = closest["name"]
        
        # Look up flight prices for this city/airport
        city_lower = str(row["city"]).lower()
        flight_matches = flights[
            (flights["destination_city"].str.lower() == city_lower) | 
            (flights["destination_iata"] == iata)
        ]
        
        avg_price = flight_matches["avg_roundtrip_usd"].mean() if not flight_matches.empty else None
        
        nearest_iata.append(iata)
        nearest_airport_name.append(name)
        flight_cost.append(round(avg_price) if avg_price and not math.isnan(avg_price) else None)
    else:
        nearest_iata.append(None)
        nearest_airport_name.append(None)
        flight_cost.append(None)

places["nearest_airport_iata"] = nearest_iata
places["nearest_airport_name"] = nearest_airport_name
places["avg_flight_price_usd"] = flight_cost

# Save back to CSV
places.to_csv(DATA_DIR / "international_places.csv", index=False, encoding="utf-8")

# Print summary
linked_airports = places["nearest_airport_iata"].notna().sum()
linked_prices = places["avg_flight_price_usd"].notna().sum()
print(f"✅ Linking complete.")
print(f" - {linked_airports}/{len(places)} places linked to a nearby airport.")
print(f" - {linked_prices}/{len(places)} places linked to flight ticket prices.")
print("="*50)
print("The Places Database is now structurally merged with the Flight Databases!")
