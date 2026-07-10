import sys, math, random
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

US_CITIES_DATA = [
    ("Los Angeles", 34.0522, -118.2437, [
        ("Hollywood Walk of Fame", "Landmark", "Famous sidewalk with stars.", 4.2, 0, 2, "Evening", "Iconic,Free", "No"),
        ("Griffith Observatory", "Museum", "Observatory with views of LA and Hollywood sign.", 4.8, 0, 3, "Sunset", "Views,Science", "No"),
        ("Santa Monica Pier", "Entertainment", "Historic pier with amusement park.", 4.5, 0, 3, "Afternoon", "Beach,Family", "No"),
    ]),
    ("Chicago", 41.8781, -87.6298, [
        ("Millennium Park", "Park", "Home to the famous Cloud Gate (The Bean).", 4.7, 0, 2, "Morning", "Art,Free", "No"),
        ("Art Institute of Chicago", "Museum", "One of the oldest and largest art museums.", 4.9, 25, 4, "Morning", "Art,Culture", "No"),
        ("Navy Pier", "Entertainment", "Lakefront attraction with rides and restaurants.", 4.4, 0, 3, "Evening", "Family,Lake", "No"),
    ]),
    ("Houston", 29.7604, -95.3698, [
        ("Space Center Houston", "Museum", "Official visitor center of NASA Johnson Space Center.", 4.7, 30, 4, "Morning", "Space,Science", "No"),
        ("Houston Museum of Natural Science", "Museum", "Features dinosaur skeletons and planetarium.", 4.8, 25, 3, "Afternoon", "Science,Family", "No"),
    ]),
    ("Phoenix", 33.4484, -112.0740, [
        ("Desert Botanical Garden", "Nature", "Showcases beautiful desert flora.", 4.7, 30, 2, "Morning", "Nature,Desert", "No"),
        ("Camelback Mountain", "Nature", "Popular hiking destination with city views.", 4.8, 0, 3, "Early morning", "Hiking,Views", "No"),
    ]),
    ("Philadelphia", 39.9526, -75.1652, [
        ("Independence Hall", "Historic", "Where the Declaration of Independence was signed.", 4.8, 0, 2, "Morning", "History,UNESCO", "Yes"),
        ("Liberty Bell", "Historic", "Iconic symbol of American independence.", 4.6, 0, 1, "Morning", "History,Free", "No"),
    ]),
    ("San Antonio", 29.4241, -98.4936, [
        ("The Alamo", "Historic", "Historic Spanish mission and fortress compound.", 4.6, 0, 2, "Morning", "History,Free", "Yes"),
        ("San Antonio River Walk", "Entertainment", "City park and network of walkways along the river.", 4.8, 0, 3, "Evening", "Scenic,Dining", "No"),
    ]),
    ("San Diego", 32.7157, -117.1611, [
        ("San Diego Zoo", "Nature", "World famous zoo in Balboa Park.", 4.8, 65, 5, "Morning", "Animals,Family", "No"),
        ("Balboa Park", "Park", "1,200-acre historic urban cultural park.", 4.8, 0, 4, "Afternoon", "Culture,Park", "No"),
    ]),
    ("Dallas", 32.7767, -96.7970, [
        ("The Sixth Floor Museum", "Museum", "Chronicles the assassination of JFK.", 4.7, 18, 2, "Morning", "History,Museum", "No"),
        ("Dallas Arboretum", "Nature", "66-acre botanical garden on White Rock Lake.", 4.8, 17, 3, "Spring", "Nature,Garden", "No"),
    ]),
    ("Austin", 30.2672, -97.7431, [
        ("Texas State Capitol", "Historic", "Historic seat of the state government.", 4.7, 0, 2, "Morning", "History,Architecture", "No"),
        ("Zilker Park", "Park", "351-acre metropolitan park.", 4.8, 0, 3, "Afternoon", "Nature,Recreation", "No"),
    ]),
    ("Seattle", 47.6062, -122.3321, [
        ("Space Needle", "Landmark", "Iconic observation tower.", 4.6, 35, 2, "Sunset", "Views,Iconic", "No"),
        ("Pike Place Market", "Shopping", "Famous public market overlooking the waterfront.", 4.7, 0, 3, "Morning", "Food,Local", "No"),
    ]),
    ("Denver", 39.7392, -104.9903, [
        ("Denver Botanic Gardens", "Nature", "23-acre public botanical garden.", 4.8, 15, 3, "Afternoon", "Nature,Garden", "No"),
        ("Red Rocks Amphitheatre", "Entertainment", "Open-air amphitheatre built into a rock structure.", 4.9, 0, 3, "Evening", "Music,Nature", "No"),
    ]),
    ("Washington", 38.9072, -77.0369, [
        ("National Mall", "Historic", "Landscaped park with iconic monuments.", 4.8, 0, 4, "Afternoon", "Monuments,History", "No"),
        ("Smithsonian National Air and Space Museum", "Museum", "Features the history of aviation and spaceflight.", 4.7, 0, 4, "Morning", "Museum,Science", "No"),
    ]),
    ("Boston", 42.3601, -71.0589, [
        ("Freedom Trail", "Historic", "2.5-mile-long path through downtown Boston.", 4.7, 0, 4, "Morning", "History,Walking", "No"),
        ("Fenway Park", "Entertainment", "Historic baseball park.", 4.8, 25, 2, "Evening", "Sports,History", "No"),
    ]),
    ("Miami", 25.7617, -80.1918, [
        ("South Beach", "Nature", "Famous beach and neighborhood.", 4.6, 0, 4, "Afternoon", "Beach,Nightlife", "No"),
        ("Vizcaya Museum and Gardens", "Museum", "Former villa and estate of businessman James Deering.", 4.7, 25, 3, "Morning", "Architecture,Garden", "No"),
    ]),
    ("Atlanta", 33.7490, -84.3880, [
        ("Georgia Aquarium", "Nature", "One of the largest aquariums in the world.", 4.7, 40, 4, "Morning", "Animals,Family", "No"),
        ("World of Coca-Cola", "Museum", "Showcases the history of The Coca-Cola Company.", 4.5, 19, 3, "Afternoon", "Museum,Pop Culture", "No"),
    ]),
    ("New Orleans", 29.9511, -90.0715, [
        ("French Quarter", "Historic", "The oldest neighborhood in the city.", 4.7, 0, 4, "Evening", "History,Nightlife", "No"),
        ("National WWII Museum", "Museum", "Military history museum.", 4.9, 30, 5, "Morning", "History,Museum", "No"),
    ]),
    ("Honolulu", 21.3069, -157.8583, [
        ("Pearl Harbor National Memorial", "Historic", "Memorial for the attack on Pearl Harbor.", 4.8, 0, 4, "Morning", "History,Memorial", "No"),
        ("Waikiki Beach", "Nature", "World famous beach.", 4.5, 0, 4, "Afternoon", "Beach,Surfing", "No"),
    ]),
    ("Charleston", 32.7765, -79.9311, [
        ("Charleston Historic District", "Historic", "Preserved architecture and historic charm.", 4.8, 0, 3, "Morning", "History,Walking", "No"),
        ("Fort Sumter", "Historic", "Sea fort where the Civil War began.", 4.6, 30, 3, "Morning", "History,Fort", "No"),
    ]),
    ("Savannah", 32.0809, -81.0912, [
        ("Forsyth Park", "Park", "Large city park with a famous fountain.", 4.8, 0, 2, "Afternoon", "Park,Scenic", "No"),
        ("Savannah Historic District", "Historic", "Known for its beautiful squares and architecture.", 4.8, 0, 4, "Morning", "History,Architecture", "No"),
    ]),
    ("Orlando", 28.5383, -81.3792, [
        ("Walt Disney World Resort", "Entertainment", "The most visited vacation resort in the world.", 4.7, 109, 8, "Morning", "Theme Park,Family", "No"),
        ("Universal Orlando Resort", "Entertainment", "Major theme park and entertainment resort complex.", 4.7, 109, 8, "Morning", "Theme Park,Movies", "No"),
    ]),
    ("Nashville", 36.1627, -86.7816, [
        ("Grand Ole Opry", "Entertainment", "Weekly country music stage concert.", 4.8, 45, 3, "Evening", "Music,Culture", "No"),
        ("Country Music Hall of Fame", "Museum", "Museum dedicated to country music.", 4.7, 28, 3, "Morning", "Music,Museum", "No"),
    ]),
    ("Portland", 45.5152, -122.6784, [
        ("Washington Park", "Park", "Includes a zoo, forestry museum, and arboretum.", 4.7, 0, 4, "Afternoon", "Nature,Park", "No"),
        ("Portland Japanese Garden", "Nature", "Considered one of the most authentic Japanese gardens outside of Japan.", 4.8, 20, 2, "Morning", "Garden,Relaxing", "No"),
    ]),
    ("Salt Lake City", 40.7608, -111.8910, [
        ("Temple Square", "Spiritual", "Center of the LDS Church.", 4.7, 0, 2, "Morning", "Architecture,Religion", "No"),
        ("Great Salt Lake", "Nature", "The largest saltwater lake in the Western Hemisphere.", 4.2, 5, 3, "Afternoon", "Nature,Lake", "No"),
    ]),
]

print("Loading existing databases...")
places = pd.read_csv(DATA_DIR / "international_places.csv", encoding="utf-8")
airports = pd.read_csv(DATA_DIR / "airports.dat", header=None, encoding="utf-8", on_bad_lines="skip",
                        names=["id","name","city","country","iata","icao","lat","lon","alt","tz","dst","tz_db","type","source"])
airports = airports[airports["iata"].notna() & (airports["iata"] != "\\N") & (airports["type"] == "airport")]
flights = pd.read_csv(DATA_DIR / "flight_price_index.csv", encoding="utf-8")

new_rows = []

for city, lat, lon, attractions in US_CITIES_DATA:
    # Find nearest airport
    country_airports = airports[airports["country"].str.lower() == "united states"].copy()
    country_airports["dist"] = country_airports.apply(lambda r: haversine(lat, lon, r["lat"], r["lon"]), axis=1)
    closest = country_airports.loc[country_airports["dist"].idxmin()] if not country_airports.empty else None
    
    iata = closest["iata"] if closest is not None else None
    name = closest["name"] if closest is not None else None
    
    # Flight price
    avg_price = None
    if iata:
        flight_matches = flights[(flights["destination_city"].str.lower() == city.lower()) | (flights["destination_iata"] == iata)]
        if not flight_matches.empty:
            avg_price = flight_matches["avg_roundtrip_usd"].mean()
    
    if avg_price and not math.isnan(avg_price):
        flight_cost = round(avg_price)
    else:
        flight_cost = None

    for att in attractions:
        new_rows.append({
            "country": "United States",
            "country_code": "US",
            "city": city,
            "place_name": att[0],
            "category": att[1],
            "description": att[2],
            "rating": att[3],
            "entry_fee_usd": att[4],
            "visit_duration_hrs": att[5],
            "best_time_to_visit": att[6],
            "tags": att[7],
            "lat": lat,
            "lon": lon,
            "is_unesco": att[8],
            "continent": "North America",
            "nearest_airport_iata": iata,
            "nearest_airport_name": name,
            "avg_flight_price_usd": flight_cost
        })

new_df = pd.DataFrame(new_rows)
# Filter out duplicates if we run this multiple times
existing_places = set(places["place_name"].str.lower())
new_df = new_df[~new_df["place_name"].str.lower().isin(existing_places)]

if not new_df.empty:
    places = pd.concat([places, new_df], ignore_index=True)
    places.to_csv(DATA_DIR / "international_places.csv", index=False, encoding="utf-8")
    print(f"✅ Added {len(new_df)} new attractions across {len(US_CITIES_DATA)} US cities.")
else:
    print("⚠️ All attractions already exist in the database.")
