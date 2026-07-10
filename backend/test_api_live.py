"""Live API integration test against the running server."""
import urllib.request, json, sys
sys.stdout.reconfigure(encoding='utf-8')

payload = json.dumps({
    "session_id": "live-test-001",
    "destination": "Bali, Indonesia",
    "start_date": "2025-09-01",
    "end_date": "2025-09-08",
    "budget_usd": 2500,
    "travelers_count": 1,
    "travel_purpose": "Adventure"
}).encode()

req = urllib.request.Request(
    "http://localhost:8000/api/trips/plan",
    data=payload,
    headers={"Content-Type": "application/json"},
    method="POST"
)

print("POST /api/trips/plan for Bali, Indonesia...")
with urllib.request.urlopen(req, timeout=60) as r:
    data = json.loads(r.read().decode())

ts = data["travel_score"]
budget = data["budget"]
hotels = data["recommended_hotels"]
flights = data["flights"]

print(f"Trip ID: {data['trip_id']}")
print(f"Destination: {data['destination']}")
print(f"Travel Score: {ts['total']:.1f}/100 - {ts['label']}")
print(f"  Weather: {ts['weather_score']:.0f}  Budget: {ts['budget_score']:.0f}  Hotels: {ts['hotel_score']:.0f}")
print(f"Hotels: {len(hotels)} options")
if hotels:
    top = hotels[0]
    print(f"  Best: {top['hotel_name']} - Score: {top['recommendation_score']:.0f}/100 - ${top['price_per_night_usd']}/night")
print(f"Flights: {len(flights)} options")
if flights:
    cheap = min(flights, key=lambda f: f["price_usd"])
    print(f"  Cheapest: {cheap['airline']} at ${cheap['price_usd']:,.0f}")
print(f"Budget: ${budget['total_estimated_usd']:,.0f} estimated")
print(f"Budget Fit: {budget['budget_fit_label']}")
print(f"Itinerary: {len(data['itinerary'])} days")
print(f"Review Insights: {len(data['review_insights'])} hotels analyzed")
print(f"Personalized Tips: {len(data['personalized_tips'])}")
print("")
print("=" * 50)
print("LIVE API TEST PASSED!")
print("=" * 50)
