"""
Script to dynamically add tourist places for almost all cities in a given country.
Usage: python add_country_places.py --country "Country Name"
"""
import sys
import argparse
import random
import math
import pandas as pd
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

DATA_DIR = Path("C:/datascience/cylsiss/backend/app/data")

def haversine(lat1, lon1, lat2, lon2):
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a)) 
    r = 6371
    return c * r

def generate_city_places(city_name, country_name, lat, lon):
    """Generate 2-3 synthetic but realistic-sounding places for a city."""
    categories = [
        ("Landmark", "Central Square", f"The historic heart of {city_name}, bustling with locals and cafes.", "Iconic,Free", "Afternoon"),
        ("Museum", "National Museum", f"Explore the deep history and culture of {country_name} in {city_name}.", "History,Culture", "Morning"),
        ("Park", "City Botanical Gardens", f"A peaceful green oasis in the middle of {city_name}.", "Nature,Relaxing", "Morning"),
        ("Spiritual", "Grand Cathedral/Temple", f"An architectural marvel and spiritual center of {city_name}.", "Architecture,Spiritual", "Morning"),
        ("Entertainment", "Downtown Entertainment District", f"The best place for food, music, and nightlife in {city_name}.", "Nightlife,Food", "Evening"),
        ("Nature", "Scenic Lookout Point", f"Panoramic views of {city_name} and its surroundings.", "Views,Nature", "Sunset")
    ]
    
    # Pick 2 or 3 random categories
    num_places = random.randint(2, 3)
    chosen = random.sample(categories, num_places)
    
    places = []
    for cat in chosen:
        places.append({
            "country": country_name,
            "country_code": "XX", # We'll fill this later or leave as XX
            "city": city_name,
            "place_name": f"{city_name} {cat[1]}",
            "category": cat[0],
            "description": cat[2],
            "rating": round(random.uniform(4.0, 4.9), 1),
            "entry_fee_usd": random.choice([0, 5, 10, 15, 25]),
            "visit_duration_hrs": random.choice([1, 2, 3]),
            "best_time_to_visit": cat[4],
            "tags": cat[3],
            "lat": lat + random.uniform(-0.02, 0.02),
            "lon": lon + random.uniform(-0.02, 0.02),
            "is_unesco": "No",
            "continent": "Unknown"
        })
    return places

def main():
    parser = argparse.ArgumentParser(description="Add tourist places for almost all cities in a country.")
    parser.add_argument("--country", type=str, required=True, help="Country name (e.g. 'United States', 'Japan')")
    args = parser.parse_args()
    target_country = args.country

    print(f"Loading databases to process '{target_country}'...")
    places_df = pd.read_csv(DATA_DIR / "international_places.csv", encoding="utf-8")
    
    # Load airports to get cities
    airports = pd.read_csv(DATA_DIR / "airports.dat", header=None, encoding="utf-8", on_bad_lines="skip",
                            names=["id","name","city","country","iata","icao","lat","lon","alt","tz","dst","tz_db","type","source"])
    airports = airports[airports["iata"].notna() & (airports["iata"] != "\\N") & (airports["type"] == "airport")]
    
    flights = pd.read_csv(DATA_DIR / "flight_price_index.csv", encoding="utf-8")

    # Filter airports by target country
    country_airports = airports[airports["country"].str.lower() == target_country.lower()]
    if country_airports.empty:
        print(f"❌ Could not find any cities for country '{target_country}' in the database.")
        sys.exit(1)
        
    unique_cities = country_airports.drop_duplicates(subset=["city"])
    print(f"Found {len(unique_cities)} unique cities in {target_country}.")
    
    # Find continent and country code if possible from existing places
    existing_country_places = places_df[places_df["country"].str.lower() == target_country.lower()]
    c_code = existing_country_places["country_code"].iloc[0] if not existing_country_places.empty else "XX"
    continent = existing_country_places["continent"].iloc[0] if not existing_country_places.empty else "Unknown"

    new_rows = []
    existing_place_names = set(places_df["place_name"].str.lower())
    
    print("Generating tourist attractions and linking flights...")
    for idx, row in unique_cities.iterrows():
        city = row["city"]
        city_lat = float(row["lat"])
        city_lon = float(row["lon"])
        
        # Generate synthetic places
        city_places = generate_city_places(city, target_country, city_lat, city_lon)
        
        for p in city_places:
            p["country_code"] = c_code
            p["continent"] = continent
            
            # Find nearest airport (this city's airport is usually the closest)
            p["nearest_airport_iata"] = row["iata"]
            p["nearest_airport_name"] = row["name"]
            
            # Find flight price
            avg_price = None
            flight_matches = flights[(flights["destination_city"].str.lower() == city.lower()) | (flights["destination_iata"] == row["iata"])]
            if not flight_matches.empty:
                avg_price = flight_matches["avg_roundtrip_usd"].mean()
            
            p["avg_flight_price_usd"] = round(avg_price) if avg_price and not math.isnan(avg_price) else None
            
            if p["place_name"].lower() not in existing_place_names:
                new_rows.append(p)
                existing_place_names.add(p["place_name"].lower())

    if new_rows:
        new_df = pd.DataFrame(new_rows)
        places_df = pd.concat([places_df, new_df], ignore_index=True)
        places_df.to_csv(DATA_DIR / "international_places.csv", index=False, encoding="utf-8")
        print(f"✅ Successfully added {len(new_rows)} tourist places across {len(unique_cities)} cities in {target_country}!")
        print("Run the backend restart command to load the new data.")
    else:
        print("⚠️ No new places to add. They might already exist.")

if __name__ == "__main__":
    main()
