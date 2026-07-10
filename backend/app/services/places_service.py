"""
Places Service — Google Places API with rich mock fallback.
Provides hotel data, review summaries, local attractions, and nearby services.
"""
import random
import logging
from typing import List, Dict, Any
from app.config import settings
from app.schemas import HotelResult, AttractionResult, ReviewInsight, NearbyService

logger = logging.getLogger(__name__)

# ── Mock Hotels ──────────────────────────────────────────────────────────────

MOCK_HOTELS_BY_DESTINATION = {
    "paris": [
        {"name": "Hôtel Le Marais Élégance",    "addr": "15 Rue de Bretagne, Paris",      "pricepn": 180, "rating": 4.7, "amenities": ["WiFi", "Breakfast", "Concierge", "Bar", "Rooftop"]},
        {"name": "Montmartre Boutique Inn",       "addr": "22 Rue Lepic, Paris",             "pricepn": 120, "rating": 4.5, "amenities": ["WiFi", "Breakfast", "Art Gallery", "Café"]},
        {"name": "Grand Hôtel Opéra",            "addr": "2 Rue Scribe, Paris",             "pricepn": 280, "rating": 4.8, "amenities": ["Spa", "Pool", "Restaurant", "Valet", "Gym", "Concierge"]},
        {"name": "Eiffel View Residence",         "addr": "8 Avenue Bosquet, Paris",         "pricepn": 210, "rating": 4.6, "amenities": ["WiFi", "Room Service", "View Terrace", "Concierge"]},
    ],
    "bali": [
        {"name": "Ubud Jungle Retreat",           "addr": "Jl. Raya Ubud, Bali",            "pricepn": 95,  "rating": 4.8, "amenities": ["Pool", "Spa", "Yoga Studio", "Organic Restaurant", "WiFi"]},
        {"name": "Seminyak Beach Villa",          "addr": "Jl. Laksmana, Seminyak",          "pricepn": 150, "rating": 4.6, "amenities": ["Private Pool", "Beach Access", "Bar", "Breakfast", "WiFi"]},
        {"name": "Uluwatu Cliff Resort",          "addr": "Jl. Labuan Sait, Uluwatu",        "pricepn": 220, "rating": 4.9, "amenities": ["Infinity Pool", "Spa", "Sunset Bar", "Fine Dining", "Yoga"]},
        {"name": "Canggu Surfer Hostel & Hotel",  "addr": "Jl. Batu Bolong, Canggu",         "pricepn": 55,  "rating": 4.3, "amenities": ["Pool", "Café", "Surf Lessons", "Coworking", "WiFi"]},
    ],
    "tokyo": [
        {"name": "Shinjuku Grand Hotel",          "addr": "2-6-1 Nishi-Shinjuku, Tokyo",     "pricepn": 160, "rating": 4.6, "amenities": ["WiFi", "Gym", "Restaurant", "Concierge", "Onsen"]},
        {"name": "Asakusa Heritage Inn",          "addr": "1-22-4 Asakusa, Tokyo",           "pricepn": 110, "rating": 4.7, "amenities": ["WiFi", "Traditional Breakfast", "Yukata Rental", "Garden"]},
        {"name": "Shibuya Modern Tower",          "addr": "21-1 Dogenzaka, Shibuya",         "pricepn": 200, "rating": 4.5, "amenities": ["Pool", "Gym", "Sky Bar", "WiFi", "Concierge"]},
        {"name": "Akihabara Tech Stay",           "addr": "1-14-3 Soto-Kanda, Tokyo",        "pricepn": 85,  "rating": 4.4, "amenities": ["WiFi", "Capsule Options", "24h Convenience", "Lounge"]},
    ],
    "dubai": [
        {"name": "Burj View Luxury Hotel",        "addr": "Sheikh Zayed Road, Dubai",        "pricepn": 350, "rating": 4.9, "amenities": ["Infinity Pool", "Spa", "Butler", "Fine Dining", "Gym"]},
        {"name": "Dubai Marina Suites",           "addr": "Dubai Marina Walk",               "pricepn": 200, "rating": 4.7, "amenities": ["Pool", "Gym", "Marina View", "WiFi", "Concierge"]},
        {"name": "Old Dubai Heritage Inn",        "addr": "Al Fahidi, Dubai Creek",          "pricepn": 110, "rating": 4.5, "amenities": ["WiFi", "Breakfast", "Cultural Tours", "Rooftop"]},
        {"name": "Palm Jumeirah Resort",          "addr": "Palm Jumeirah, Dubai",            "pricepn": 480, "rating": 4.8, "amenities": ["Private Beach", "Spa", "Multiple Restaurants", "Water Sports"]},
    ],
    "london": [
        {"name": "Covent Garden Boutique",        "addr": "King Street, Covent Garden",      "pricepn": 220, "rating": 4.6, "amenities": ["WiFi", "Breakfast", "Bar", "Concierge"]},
        {"name": "Tower Bridge Hotel",            "addr": "Tooley Street, London Bridge",    "pricepn": 280, "rating": 4.7, "amenities": ["Pool", "Gym", "Spa", "Restaurant", "WiFi"]},
        {"name": "Notting Hill B&B",              "addr": "Pembridge Road, London",          "pricepn": 150, "rating": 4.5, "amenities": ["WiFi", "Breakfast", "Garden", "Bicycle Rental"]},
        {"name": "Mayfair Grand Hotel",           "addr": "Park Lane, Mayfair",              "pricepn": 420, "rating": 4.9, "amenities": ["Spa", "Fine Dining", "Concierge", "Valet", "Gym"]},
    ],
    "default": [
        {"name": "City Central Grand Hotel",      "addr": "1 Main Boulevard",                "pricepn": 150, "rating": 4.5, "amenities": ["WiFi", "Pool", "Restaurant", "Gym", "Concierge"]},
        {"name": "Boutique Heritage Inn",         "addr": "Old Town Square",                 "pricepn": 95,  "rating": 4.6, "amenities": ["WiFi", "Breakfast", "Garden", "Bar"]},
        {"name": "Luxury Skyline Resort",         "addr": "45 Skyline Drive",                "pricepn": 260, "rating": 4.8, "amenities": ["Infinity Pool", "Spa", "Fine Dining", "Valet", "Gym", "Rooftop Bar"]},
        {"name": "Budget Comfort Stay",           "addr": "22 Station Road",                 "pricepn": 65,  "rating": 4.2, "amenities": ["WiFi", "Breakfast", "Parking"]},
        {"name": "Riverside Boutique Hotel",      "addr": "8 River Walk",                    "pricepn": 130, "rating": 4.4, "amenities": ["WiFi", "Pool", "Terrace", "Bar", "Bicycle Rental"]},
    ],
}

# ── Mock Attractions ─────────────────────────────────────────────────────────

MOCK_ATTRACTIONS = {
    "paris": [
        AttractionResult(name="Eiffel Tower",           category="Landmark",   rating=4.9, description="Iconic iron lattice tower offering panoramic views of Paris from 276m high.",           estimated_duration_hours=2.5, entry_fee_usd=26, tags=["Iconic", "Views", "Photography"], best_time_to_visit="Early morning or evening"),
        AttractionResult(name="Louvre Museum",           category="Museum",     rating=4.8, description="World's largest art museum housing the Mona Lisa and Venus de Milo.",                  estimated_duration_hours=4.0, entry_fee_usd=17, tags=["Art", "History", "Culture"], best_time_to_visit="Weekday mornings"),
        AttractionResult(name="Palace of Versailles",    category="Historical", rating=4.7, description="Opulent royal château with magnificent Hall of Mirrors and vast gardens.",              estimated_duration_hours=5.0, entry_fee_usd=20, tags=["Royal", "Gardens", "History"], best_time_to_visit="Tuesday–Thursday"),
        AttractionResult(name="Montmartre & Sacré-Cœur", category="Cultural",  rating=4.6, description="Charming hilltop district with artists, cafés, cobblestone streets and the white basilica.", estimated_duration_hours=3.0, entry_fee_usd=0, tags=["Art", "Free", "Views"], best_time_to_visit="Morning"),
        AttractionResult(name="Seine River Cruise",      category="Landmark",   rating=4.7, description="Relaxing boat cruise along the Seine passing Notre-Dame, Louvre and Eiffel Tower.",    estimated_duration_hours=1.5, entry_fee_usd=15, tags=["Romantic", "Scenic", "Relaxing"], best_time_to_visit="Sunset"),
        AttractionResult(name="Centre Pompidou",         category="Museum",     rating=4.5, description="Inside-out modern art museum with Europe's largest collection of modern art.",          estimated_duration_hours=3.0, entry_fee_usd=14, tags=["Modern Art", "Architecture"], best_time_to_visit="Afternoon"),
    ],
    "bali": [
        AttractionResult(name="Tanah Lot Temple",         category="Spiritual",  rating=4.8, description="Ancient sea temple perched on an offshore rock, most dramatic at sunset.",              estimated_duration_hours=2.0, entry_fee_usd=4,  tags=["Temple", "Sunset", "Spiritual"], best_time_to_visit="Sunset (5–6 PM)"),
        AttractionResult(name="Ubud Monkey Forest",       category="Nature",     rating=4.6, description="Sacred nature reserve with 700+ Balinese long-tailed monkeys among ancient temples.",   estimated_duration_hours=1.5, entry_fee_usd=5,  tags=["Wildlife", "Forest", "Temple"], best_time_to_visit="Morning"),
        AttractionResult(name="Mount Batur Sunrise Trek", category="Adventure",  rating=4.9, description="Active volcano trek for breathtaking sunrise views above the clouds at 1,717m.",       estimated_duration_hours=6.0, entry_fee_usd=35, tags=["Trekking", "Sunrise", "Volcano"], best_time_to_visit="2 AM start"),
        AttractionResult(name="Tegallalang Rice Terraces",category="Nature",     rating=4.7, description="UNESCO-listed emerald rice terraces with traditional subak irrigation system.",         estimated_duration_hours=2.0, entry_fee_usd=2,  tags=["Nature", "Photography", "Heritage"], best_time_to_visit="Early morning"),
        AttractionResult(name="Uluwatu Temple",           category="Spiritual",  rating=4.7, description="Dramatic clifftop sea temple with resident monkeys and traditional Kecak fire dance.",   estimated_duration_hours=2.5, entry_fee_usd=5,  tags=["Temple", "Dance", "Cliffs"], best_time_to_visit="Sunset for Kecak dance"),
        AttractionResult(name="Seminyak Beach",           category="Nature",     rating=4.6, description="Trendy beach with world-class surf breaks, beach clubs and luxury resorts.",             estimated_duration_hours=3.0, entry_fee_usd=0,  tags=["Beach", "Surf", "Free"], best_time_to_visit="Afternoon–sunset"),
    ],
    "tokyo": [
        AttractionResult(name="Senso-ji Temple",          category="Spiritual",  rating=4.8, description="Tokyo's oldest temple in Asakusa with Nakamise shopping street leading to the gate.",   estimated_duration_hours=2.0, entry_fee_usd=0,  tags=["Temple", "Free", "Historic"], best_time_to_visit="Early morning"),
        AttractionResult(name="Shibuya Crossing",         category="Landmark",   rating=4.9, description="World's busiest pedestrian crossing — an unmissable Tokyo spectacle.",                  estimated_duration_hours=0.5, entry_fee_usd=0,  tags=["Iconic", "Free", "Photography"], best_time_to_visit="Evening rush"),
        AttractionResult(name="TeamLab Borderless",       category="Museum",     rating=4.8, description="Futuristic digital art museum with immersive light and sound installations.",            estimated_duration_hours=3.0, entry_fee_usd=32, tags=["Digital Art", "Immersive", "Unique"], best_time_to_visit="Weekday"),
        AttractionResult(name="Meiji Shrine",             category="Spiritual",  rating=4.7, description="Tranquil forested Shinto shrine dedicated to Emperor Meiji in central Tokyo.",          estimated_duration_hours=1.5, entry_fee_usd=0,  tags=["Shrine", "Free", "Forest"], best_time_to_visit="Morning"),
        AttractionResult(name="Tsukiji Outer Market",     category="Food & Culture", rating=4.7, description="Historic fish market with hundreds of stalls serving the freshest sushi and seafood.", estimated_duration_hours=2.0, entry_fee_usd=0, tags=["Food", "Market", "Sushi"], best_time_to_visit="Early morning"),
        AttractionResult(name="Akihabara Electric Town",  category="Cultural",   rating=4.5, description="Neon-lit electronics and anime district — the heart of Japanese pop culture.",           estimated_duration_hours=3.0, entry_fee_usd=0,  tags=["Shopping", "Anime", "Tech"], best_time_to_visit="Afternoon"),
    ],
    "dubai": [
        AttractionResult(name="Burj Khalifa",             category="Landmark",   rating=4.8, description="World's tallest building at 828m — observation deck offers unreal 360° views.",         estimated_duration_hours=2.0, entry_fee_usd=35, tags=["Iconic", "Views", "Architecture"], best_time_to_visit="Sunset"),
        AttractionResult(name="Dubai Mall",               category="Cultural",   rating=4.7, description="World's largest mall with an aquarium, ice rink, and 1,200+ shops.",                    estimated_duration_hours=4.0, entry_fee_usd=0,  tags=["Shopping", "Free Entry", "Aquarium"], best_time_to_visit="Evening"),
        AttractionResult(name="Dubai Creek & Old Souks",  category="Historical", rating=4.6, description="Historic waterway with gold and spice souks — the soul of old Dubai.",                  estimated_duration_hours=3.0, entry_fee_usd=1,  tags=["History", "Market", "Culture"], best_time_to_visit="Morning"),
        AttractionResult(name="Desert Safari",            category="Adventure",  rating=4.9, description="Dune bashing, camel rides, sandboarding and Bedouin camp dinner under the stars.",      estimated_duration_hours=6.0, entry_fee_usd=60, tags=["Adventure", "Desert", "Cultural"], best_time_to_visit="Afternoon–evening"),
        AttractionResult(name="Palm Jumeirah",            category="Landmark",   rating=4.7, description="World-famous artificial archipelago visible from space — monorail and beach access.",    estimated_duration_hours=3.0, entry_fee_usd=5,  tags=["Iconic", "Beach", "Views"], best_time_to_visit="Any time"),
    ],
    "london": [
        AttractionResult(name="British Museum",           category="Museum",     rating=4.8, description="Free world-class museum housing the Rosetta Stone and Egyptian mummies.",                estimated_duration_hours=4.0, entry_fee_usd=0,  tags=["Museum", "Free", "History"], best_time_to_visit="Weekday morning"),
        AttractionResult(name="Tower of London",          category="Historical", rating=4.7, description="900-year-old fortress housing the Crown Jewels and Beefeater guards.",                   estimated_duration_hours=3.0, entry_fee_usd=34, tags=["History", "Crown Jewels", "Castle"], best_time_to_visit="Morning"),
        AttractionResult(name="Buckingham Palace",        category="Landmark",   rating=4.6, description="Official royal residence with Changing of the Guard ceremony.",                          estimated_duration_hours=2.0, entry_fee_usd=30, tags=["Royal", "Iconic", "Photography"], best_time_to_visit="11 AM (guard change)"),
        AttractionResult(name="Camden Market",            category="Cultural",   rating=4.6, description="Eclectic market with street food from 50+ countries, vintage fashion and live music.",   estimated_duration_hours=3.0, entry_fee_usd=0,  tags=["Market", "Food", "Free"], best_time_to_visit="Weekend afternoon"),
        AttractionResult(name="Hyde Park",                category="Nature",     rating=4.7, description="350-acre royal park with Serpentine Gallery, boating and open-air concerts.",            estimated_duration_hours=2.5, entry_fee_usd=0,  tags=["Park", "Free", "Nature"], best_time_to_visit="Morning"),
    ],
    "default": [
        AttractionResult(name="City Historic Centre",     category="Cultural",   rating=4.6, description="Explore the rich history and architecture of the city's old quarter — free walking tour.", estimated_duration_hours=3.0, entry_fee_usd=0,  tags=["History", "Free", "Walking"]),
        AttractionResult(name="National Museum",          category="Museum",     rating=4.5, description="Comprehensive museum showcasing the region's art, history and cultural heritage.",         estimated_duration_hours=2.5, entry_fee_usd=12, tags=["Culture", "Art", "History"]),
        AttractionResult(name="City Panoramic Viewpoint", category="Landmark",   rating=4.7, description="Breathtaking elevated viewpoint with sweeping city and countryside views.",               estimated_duration_hours=1.5, entry_fee_usd=5,  tags=["Views", "Photography", "Scenic"]),
        AttractionResult(name="Local Market & Food Tour", category="Food & Culture", rating=4.8, description="Vibrant local market with fresh produce, street food stalls and artisan crafts.",    estimated_duration_hours=2.0, entry_fee_usd=20, tags=["Food", "Local", "Street Food"]),
        AttractionResult(name="Botanical Garden",         category="Nature",     rating=4.4, description="Peaceful garden with thousands of plant species, ponds and shaded walking trails.",      estimated_duration_hours=2.0, entry_fee_usd=8,  tags=["Nature", "Relaxing", "Garden"]),
        AttractionResult(name="Waterfront Promenade",     category="Landmark",   rating=4.5, description="Scenic waterfront walk with cafés, street performers and sunset views.",                 estimated_duration_hours=2.0, entry_fee_usd=0,  tags=["Scenic", "Free", "Relaxing"]),
    ],
}

# ── Mock Nearby Services ─────────────────────────────────────────────────────

MOCK_NEARBY_SERVICES = {
    "paris": [
        NearbyService(name="Café de Flore", service_type="cafe", category_icon="☕", rating=4.6, distance_m=220, price_level="$$", description="Legendary Left Bank café frequented by writers and artists since 1887.", tags=["Iconic", "Historic", "Coffee"]),
        NearbyService(name="Le Grand Bistro", service_type="restaurant", category_icon="🍽️", rating=4.7, distance_m=180, price_level="$$$", description="Classic French brasserie serving escargot, duck confit and crème brûlée.", tags=["French Cuisine", "Fine Dining"]),
        NearbyService(name="La Boulangerie du Coin", service_type="cafe", category_icon="🥐", rating=4.8, distance_m=90, price_level="$", description="Award-winning neighbourhood bakery with fresh croissants from 7 AM daily.", tags=["Breakfast", "Bakery", "Budget"]),
        NearbyService(name="Hôpital Hôtel-Dieu", service_type="hospital", category_icon="🏥", rating=4.3, distance_m=850, price_level="", description="Central Paris public hospital, 24/7 emergency department. Nearest major medical facility.", tags=["Emergency", "24/7"]),
        NearbyService(name="BNP Paribas ATM", service_type="atm", category_icon="🏧", rating=4.2, distance_m=120, price_level="", description="Multi-currency ATM accepting all major international cards. Open 24/7.", tags=["24/7", "Multi-currency"]),
        NearbyService(name="Pharmacie du Louvre", service_type="pharmacy", category_icon="💊", rating=4.5, distance_m=300, price_level="$", description="English-speaking pharmacy with travel medications, sunscreen and first-aid supplies.", tags=["English Spoken", "Travel Meds"]),
        NearbyService(name="Taxi Paris Station", service_type="taxi", category_icon="🚕", rating=4.4, distance_m=200, price_level="$$", description="Official Paris taxi rank available 24/7. Book via G7 or Cab app for fixed fares.", tags=["24/7", "Airport Transfer"]),
        NearbyService(name="Marché Bio Raspail", service_type="supermarket", category_icon="🛒", rating=4.6, distance_m=500, price_level="$$", description="Famous Sunday organic market with local cheeses, wines, charcuterie and produce.", tags=["Organic", "Local", "Sunday"]),
        NearbyService(name="Le Marais Spa", service_type="spa", category_icon="💆", rating=4.7, distance_m=400, price_level="$$$", description="Boutique wellness spa offering traditional French treatments and aromatherapy.", tags=["Luxury", "Wellness", "Couples"]),
        NearbyService(name="Mosque of Paris", service_type="mosque", category_icon="🕌", rating=4.7, distance_m=1200, price_level="", description="Historic 1926 mosque with a beautiful courtyard, tea salon and hammam open to visitors.", tags=["Cultural", "Historic", "Tea House"]),
    ],
    "bali": [
        NearbyService(name="Warung Babi Guling Ibu Oka", service_type="restaurant", category_icon="🍽️", rating=4.8, distance_m=150, price_level="$", description="World-famous Balinese suckling pig warung — a must-try local institution in Ubud.", tags=["Local", "Authentic", "Budget"]),
        NearbyService(name="Kopi Luwak Café Ubud", service_type="cafe", category_icon="☕", rating=4.6, distance_m=200, price_level="$$", description="Experience the world's most famous coffee made from civet-processed beans.", tags=["Unique", "Coffee", "Experience"]),
        NearbyService(name="BIMC Hospital Nusa Dua", service_type="hospital", category_icon="🏥", rating=4.5, distance_m=2500, price_level="", description="International-standard private hospital with English-speaking doctors, 24/7 emergency.", tags=["International", "English", "24/7"]),
        NearbyService(name="Bank Mandiri ATM", service_type="atm", category_icon="🏧", rating=4.1, distance_m=180, price_level="", description="Accepts Visa, Mastercard, and international debit cards. Good exchange rate.", tags=["Visa", "Mastercard"]),
        NearbyService(name="Apotek Century Pharmacy", service_type="pharmacy", category_icon="💊", rating=4.4, distance_m=350, price_level="$", description="Well-stocked pharmacy with Western medicines, mosquito repellent and sunscreen.", tags=["Mosquito Repellent", "Sunscreen"]),
        NearbyService(name="Bluebird Taxi Stand", service_type="taxi", category_icon="🚕", rating=4.5, distance_m=100, price_level="$", description="Reliable metered taxi. Bluebird is the most trusted brand in Bali — avoid unmarked cabs.", tags=["Reliable", "Metered", "Safe"]),
        NearbyService(name="Ubud Traditional Market", service_type="supermarket", category_icon="🛒", rating=4.6, distance_m=250, price_level="$", description="Vibrant morning market (best before 9 AM) with fresh fruit, spices, batik and souvenirs.", tags=["Morning Only", "Souvenirs", "Local"]),
        NearbyService(name="The Yoga Barn", service_type="spa", category_icon="🧘", rating=4.8, distance_m=600, price_level="$$", description="World-class yoga retreat centre offering classes, spa treatments and organic café.", tags=["Yoga", "Wellness", "Detox"]),
    ],
    "tokyo": [
        NearbyService(name="Ichiran Ramen", service_type="restaurant", category_icon="🍽️", rating=4.8, distance_m=200, price_level="$", description="Famous 24/7 solo-dining ramen chain — private booths, rich tonkotsu broth.", tags=["Ramen", "24/7", "Iconic"]),
        NearbyService(name="Doutor Coffee", service_type="cafe", category_icon="☕", rating=4.3, distance_m=80, price_level="$", description="Budget-friendly Japanese coffee chain — great for quick breakfast and matcha drinks.", tags=["Budget", "Quick", "Matcha"]),
        NearbyService(name="St. Luke's International Hospital", service_type="hospital", category_icon="🏥", rating=4.6, distance_m=1800, price_level="", description="Top-rated Tokyo hospital with English-speaking staff and international patient services.", tags=["English", "International", "24/7"]),
        NearbyService(name="7-Eleven ATM", service_type="atm", category_icon="🏧", rating=4.5, distance_m=50, price_level="", description="Japan Post / 7-Bank ATM inside 7-Eleven — accepts all international cards, English interface.", tags=["24/7", "All Cards", "English"]),
        NearbyService(name="Matsumoto Kiyoshi Pharmacy", service_type="pharmacy", category_icon="💊", rating=4.5, distance_m=300, price_level="$", description="Japan's largest pharmacy chain — famous for skincare, vitamin patches and OTC medications.", tags=["Skincare", "OTC", "Popular"]),
        NearbyService(name="JapanTaxi App Stand", service_type="taxi", category_icon="🚕", rating=4.4, distance_m=150, price_level="$$", description="Book via JapanTaxi or GO app. All cabs metered, clean and professional drivers.", tags=["App Booking", "Professional", "Safe"]),
        NearbyService(name="Lawson Convenience Store", service_type="supermarket", category_icon="🛒", rating=4.6, distance_m=30, price_level="$", description="Japan's legendary convenience store — 24/7, hot meals, fresh sushi and travel essentials.", tags=["24/7", "Hot Food", "Cheap"]),
        NearbyService(name="Tokyo Onsen & Spa", service_type="spa", category_icon="♨️", rating=4.7, distance_m=800, price_level="$$", description="Authentic public bath house with natural hot spring water — a true Japanese experience.", tags=["Onsen", "Authentic", "Relaxing"]),
        NearbyService(name="Tokyo Mosque (Camii)", service_type="mosque", category_icon="🕌", rating=4.8, distance_m=3000, price_level="", description="Japan's largest mosque in Yoyogi — beautiful Turkish architecture, open to visitors.", tags=["Cultural", "Turkish Architecture"]),
    ],
    "default": [
        NearbyService(name="Local Street Food Market", service_type="restaurant", category_icon="🍽️", rating=4.6, distance_m=200, price_level="$", description="Popular local market with authentic street food stalls — ideal for a budget-friendly meal.", tags=["Street Food", "Local", "Budget"]),
        NearbyService(name="Central Café & Bakery", service_type="cafe", category_icon="☕", rating=4.4, distance_m=150, price_level="$", description="Cosy neighbourhood café serving local coffee blends, fresh pastries and light meals.", tags=["Coffee", "Breakfast", "Cosy"]),
        NearbyService(name="City General Hospital", service_type="hospital", category_icon="🏥", rating=4.2, distance_m=1200, price_level="", description="Main public hospital with emergency department. Carry your travel insurance card.", tags=["Emergency", "Public"]),
        NearbyService(name="International ATM", service_type="atm", category_icon="🏧", rating=4.1, distance_m=100, price_level="", description="Accepts Visa, Mastercard, Maestro and international debit cards. Available 24/7.", tags=["24/7", "International"]),
        NearbyService(name="City Pharmacy", service_type="pharmacy", category_icon="💊", rating=4.3, distance_m=300, price_level="$", description="Well-stocked pharmacy with travel medications, first-aid supplies and health products.", tags=["Travel Meds", "First Aid"]),
        NearbyService(name="Official Taxi Stand", service_type="taxi", category_icon="🚕", rating=4.2, distance_m=200, price_level="$$", description="Licensed metered taxis — always use official cabs or a ride-hailing app for safety.", tags=["Licensed", "Metered", "Safe"]),
        NearbyService(name="Local Supermarket", service_type="supermarket", category_icon="🛒", rating=4.3, distance_m=400, price_level="$", description="Neighbourhood supermarket with local produce, snacks, drinks and daily essentials.", tags=["Groceries", "Local", "Daily"]),
        NearbyService(name="Wellness & Massage Centre", service_type="spa", category_icon="💆", rating=4.5, distance_m=500, price_level="$$", description="Relaxing massage and wellness centre offering traditional local treatments and body scrubs.", tags=["Massage", "Relaxing", "Affordable"]),
        NearbyService(name="Local Mosque / Place of Worship", service_type="mosque", category_icon="🕌", rating=4.5, distance_m=600, price_level="", description="Community place of worship — visitors welcome with modest dress. Check prayer times.", tags=["Cultural", "Spiritual"]),
        NearbyService(name="Popular Restaurant Row", service_type="restaurant", category_icon="🍽️", rating=4.5, distance_m=350, price_level="$$", description="A strip of popular restaurants covering local and international cuisine.", tags=["Variety", "Dine-out"]),
    ],
}

PROS_POOL = [
    "Exceptional cleanliness and hygiene standards",
    "Incredibly helpful and friendly staff",
    "Prime location — walking distance to major attractions",
    "Outstanding breakfast buffet with local specialties",
    "Spacious and well-appointed rooms",
    "Fast and reliable WiFi throughout the property",
    "Excellent value for money",
    "Beautiful and tranquil pool area",
    "Superb in-house restaurant",
    "Smooth and efficient check-in process",
]

CONS_POOL = [
    "Street-facing rooms can be noisy at night",
    "Limited parking — advance booking recommended",
    "Small fitness center could use more equipment",
    "Air conditioning took time to cool the room",
    "Limited vegetarian options at breakfast",
    "Pool closes relatively early (9 PM)",
    "Elevators can be slow during peak hours",
]

COMPLAINT_POOL = [
    "WiFi speed inconsistency in upper floors",
    "Room service takes longer than expected",
    "Bathroom could use better waterproofing",
    "Noise from adjacent bar on weekends",
]


def _get_destination_key(destination: str) -> str:
    dest_lower = destination.lower()
    for key in MOCK_HOTELS_BY_DESTINATION:
        if key != "default" and key in dest_lower:
            return key
    return "default"


def _generate_review_insight(hotel_name: str, rating: float, sentiment: float) -> ReviewInsight:
    random.seed(hash(hotel_name) % 1000)
    pos_pct = round(sentiment * 100, 1)
    neg_pct = round(random.uniform(5, 20), 1)
    neu_pct = round(100 - pos_pct - neg_pct, 1)
    pros = random.sample(PROS_POOL, k=min(4, len(PROS_POOL)))
    cons = random.sample(CONS_POOL, k=min(2, len(CONS_POOL)))
    complaints = random.sample(COMPLAINT_POOL, k=min(2, len(COMPLAINT_POOL)))

    return ReviewInsight(
        hotel_name=hotel_name,
        total_reviews=random.randint(150, 2500),
        positive_pct=pos_pct,
        negative_pct=max(0, neg_pct),
        neutral_pct=max(0, neu_pct),
        top_pros=pros,
        top_cons=cons,
        recurring_complaints=complaints,
        ai_summary=f"{hotel_name} consistently receives praise for its {pros[0].lower()} and {pros[1].lower()}. "
                   f"Most guests rate their stay highly, with {pos_pct}% of reviews being positive. "
                   f"Minor concerns include {cons[0].lower()}.",
        sentiment_score=round(sentiment, 3),
    )

import httpx
import urllib.parse
from cachetools import TTLCache

wiki_image_cache = TTLCache(maxsize=200, ttl=86400)

async def fetch_wiki_image(place_name: str) -> str:
    if place_name in wiki_image_cache:
        return wiki_image_cache[place_name]
    
    fallback_img = f"https://picsum.photos/seed/{abs(hash(place_name))}/800/500"
    
    try:
        q = urllib.parse.quote(place_name)
        url = f'https://en.wikipedia.org/w/api.php?action=query&prop=pageimages&format=json&piprop=original&titles={q}'
        async with httpx.AsyncClient(headers={'User-Agent': 'Mozilla/5.0'}, verify=False) as client:
            resp = await client.get(url, timeout=4.0)
            data = resp.json()
            pages = data['query']['pages']
            for page_id in pages:
                if 'original' in pages[page_id]:
                    img = pages[page_id]['original']['source']
                    wiki_image_cache[place_name] = img
                    return img
    except Exception:
        pass
    
    # Try fallback to last word
    try:
        fallback = place_name.split()[-1]
        q = urllib.parse.quote(fallback)
        url = f'https://en.wikipedia.org/w/api.php?action=query&prop=pageimages&format=json&piprop=original&titles={q}'
        async with httpx.AsyncClient(headers={'User-Agent': 'Mozilla/5.0'}, verify=False) as client:
            resp = await client.get(url, timeout=4.0)
            data = resp.json()
            pages = data['query']['pages']
            for page_id in pages:
                if 'original' in pages[page_id]:
                    img = pages[page_id]['original']['source']
                    wiki_image_cache[place_name] = img
                    return img
    except Exception:
        pass

    wiki_image_cache[place_name] = fallback_img
    return fallback_img

async def get_hotels(destination: str, budget_per_night: float = None) -> List[HotelResult]:
    """Fetch hotel recommendations for destination."""
    if not settings.USE_MOCK_PLACES and settings.GOOGLE_PLACES_API_KEY:
        logger.info("Real Google Places API not yet implemented; using mock data.")
    return await _generate_mock_hotels_async(destination, budget_per_night)


async def _generate_mock_hotels_async(destination: str, budget_per_night: float = None) -> List[HotelResult]:
    key = _get_destination_key(destination)
    hotel_templates = MOCK_HOTELS_BY_DESTINATION.get(key, MOCK_HOTELS_BY_DESTINATION["default"])

    results = []
    random.seed(hash(destination) % 1000)

    for tmpl in hotel_templates:
        sentiment = round(random.uniform(0.72, 0.97), 3)
        rating = tmpl["rating"]
        price = tmpl["pricepn"]

        if budget_per_night:
            ratio = price / budget_per_night
            budget_fit = max(0, min(100, (1 - max(0, ratio - 1)) * 100))
        else:
            budget_fit = 75.0

        rec_score = round(
            rating / 5 * 30 +
            budget_fit / 100 * 25 +
            sentiment * 25 +
            random.uniform(0.5, 1.0) * 10 +
            random.uniform(0.7, 1.0) * 10
        , 1)

        results.append(HotelResult(
            hotel_name=tmpl["name"],
            address=tmpl["addr"],
            price_per_night_usd=price,
            rating=rating,
            sentiment_score=sentiment,
            recommendation_score=min(100, rec_score),
            budget_fit_score=budget_fit,
            pros=random.sample(PROS_POOL, k=3),
            cons=random.sample(CONS_POOL, k=2),
            amenities=tmpl["amenities"],
            image_url=f"https://picsum.photos/seed/{abs(hash(tmpl['name']))}/800/500",
            review_summary=f"Consistently praised for location and service. {int(sentiment*100)}% positive reviews.",
            is_recommended=(rec_score >= 75),
        ))

    results.sort(key=lambda x: x.recommendation_score, reverse=True)
    return results


async def get_attractions(destination: str) -> List[AttractionResult]:
    """Fetch local attractions for destination from real DB."""
    from app.services.data_manager import data_manager
    data_manager.load()
    
    db_places = data_manager.get_attractions(destination)
    if not db_places:
        key = _get_destination_key(destination)
        mock_list = MOCK_ATTRACTIONS.get(key, MOCK_ATTRACTIONS["default"])
        for m in mock_list:
            if not m.image_url or "picsum" in m.image_url:
                m.image_url = await fetch_wiki_image(m.name)
            # Add small random jitter for authentic looking ratings
            jitter = round(random.uniform(-0.1, 0.1), 1)
            m.rating = max(1.0, min(5.0, m.rating + jitter))
        return mock_list

    results = []
    for p in db_places:
        tags_str = str(p.get("tags", ""))
        tags = [t.strip() for t in tags_str.split(",") if t.strip()]
        
        name = p.get("place_name", "Unknown")
        base_rating = float(p.get("rating", 4.5))
        jittered_rating = max(1.0, min(5.0, round(base_rating + random.uniform(-0.1, 0.1), 1)))
        
        results.append(AttractionResult(
            name=name,
            category=p.get("category", "Landmark"),
            rating=jittered_rating,
            description=p.get("description", ""),
            estimated_duration_hours=float(p.get("visit_duration_hrs", 2.0)),
            entry_fee_usd=float(p.get("entry_fee_usd", 0.0)),
            tags=tags,
            best_time_to_visit=p.get("best_time_to_visit", "Any time"),
            image_url=await fetch_wiki_image(name)
        ))
        
    return results


async def get_nearby_services(destination: str) -> List[NearbyService]:
    """Fetch nearby services (restaurants, cafes, hospitals, ATMs, etc.)."""
    key = _get_destination_key(destination)
    services = MOCK_NEARBY_SERVICES.get(key, MOCK_NEARBY_SERVICES["default"])
    return services


async def get_review_insights(destination: str, hotels: List[HotelResult]) -> List[ReviewInsight]:
    """Generate review insights for each recommended hotel."""
    return [
        _generate_review_insight(h.hotel_name, h.rating, h.sentiment_score)
        for h in hotels
    ]
