"""Fresh test to verify nearby_services are included in new trip results."""
import urllib.request, json, sys
sys.stdout.reconfigure(encoding='utf-8')

payload = json.dumps({
    "session_id": "fresh-test-002",
    "destination": "Tokyo, Japan",
    "budget_usd": 3000,
    "travelers_count": 2,
    "travel_purpose": "Cultural"
}).encode()

req = urllib.request.Request(
    "http://localhost:8505/api/trips/plan",
    data=payload,
    headers={"Content-Type": "application/json"},
    method="POST"
)

print("Planning trip to Tokyo, Japan...")
with urllib.request.urlopen(req, timeout=50) as r:
    data = json.loads(r.read().decode())

print(f"Trip ID: {data['trip_id']}")
print(f"Travel Score: {data['travel_score']['total']:.1f}/100")

attrs = data.get("attractions", [])
print(f"\nAttractions: {len(attrs)}")
for a in attrs[:4]:
    tags = ", ".join(a.get("tags", []))
    print(f"  [{a['category']:12}] {a['name']} | Tags: {tags} | Best: {a.get('best_time_to_visit','')}")

svcs = data.get("nearby_services", [])
print(f"\nNearby Services: {len(svcs)}")
for s in svcs[:6]:
    print(f"  {s['category_icon']} {s['name']} ({s['service_type']}) | {s['distance_m']}m | Rating: {s['rating']}")

print("\n" + "="*55)
if len(svcs) > 0:
    print("SUCCESS: Nearby services are included in API response!")
else:
    print("WARNING: nearby_services still empty - check agent logs")
print("="*55)
