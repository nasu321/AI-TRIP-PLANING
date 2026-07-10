"""
Page 7: User Profile — persona, preferences, trip history, personalized tips.
"""
import streamlit as st
import requests
from pathlib import Path

st.set_page_config(page_title="My Profile | AI Travel", page_icon="👤", layout="wide")

css_path = Path(__file__).parent.parent / "assets" / "style.css"
if css_path.exists():
    with open(css_path, encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

st.markdown("""<style>
.stApp { background: linear-gradient(135deg, #0f0c29 0%, #1a1a2e 40%, #16213e 100%); color: #f8fafc; }
section[data-testid="stSidebar"] { background: linear-gradient(180deg, #0f0c29, #1a1a2e); }
h1,h2,h3 { color: #f8fafc; font-family: 'Space Grotesk', sans-serif; }
p, label { color: #cbd5e1; }
.stButton > button { background: linear-gradient(135deg, #7c3aed, #0ea5e9); color: white;
    border: none; border-radius: 10px; font-weight: 600; padding: 12px 24px; width: 100%; }
.stButton > button:hover { transform: translateY(-2px); }
.stTextInput > div > div > input, .stSelectbox > div > div, .stMultiSelect > div {
    background: rgba(22,33,62,0.8) !important; border: 1px solid rgba(255,255,255,0.15) !important;
    color: #f8fafc !important; border-radius: 10px !important; }
div[data-testid="stMetricValue"] { color: #7c3aed !important; font-size: 1.6rem !important; }
</style>""", unsafe_allow_html=True)

BACKEND_URL = st.session_state.get("backend_url", "http://127.0.0.1:8000")
SESSION_ID = st.session_state.get("session_id", "demo")

st.markdown("""
<div class='destination-hero'>
    <h1>👤 My Travel Profile</h1>
    <p>Your AI-classified travel persona, preferences, and trip history</p>
</div>
""", unsafe_allow_html=True)

# ─── Load profile ─────────────────────────────────────────────
result = st.session_state.get("trip_result")
persona = None
trip_count = 0

try:
    resp = requests.get(f"{BACKEND_URL}/api/users/{SESSION_ID}", timeout=10)
    if resp.status_code == 200:
        profile = resp.json()
        persona = profile.get("persona")
        trip_count = profile.get("trip_count", 0)
except Exception:
    pass

# ─── Persona Display ──────────────────────────────────────────
PERSONA_INFO = {
    "Adventure": {"icon": "🧗", "color": "#f5a623", "desc": "Thrills and natural landscapes define your ideal trip."},
    "Luxury": {"icon": "👑", "color": "#f5a623", "desc": "You seek premium experiences — top-tier hotels and exclusive access."},
    "Budget": {"icon": "💰", "color": "#10b981", "desc": "You maximize experiences while minimizing spend."},
    "Cultural": {"icon": "🎭", "color": "#7c3aed", "desc": "Museums, local customs, and historic sites are your priority."},
    "Relaxation": {"icon": "🏖️", "color": "#0ea5e9", "desc": "Rest and rejuvenation — beaches, spas, and serene environments."},
    "Family": {"icon": "👨‍👩‍👧‍👦", "color": "#f5a623", "desc": "Creating lasting memories with loved ones."},
    "Solo": {"icon": "🎒", "color": "#e94560", "desc": "Freedom, flexibility, and self-discovery."},
    "Business": {"icon": "💼", "color": "#64748b", "desc": "Efficient travel with productivity in mind."},
}

p_col1, p_col2 = st.columns([1, 2])

with p_col1:
    persona_data = PERSONA_INFO.get(persona or "Cultural", PERSONA_INFO["Cultural"])
    st.markdown(f"""
    <div style='background:linear-gradient(135deg,rgba(124,58,237,0.2),rgba(14,165,233,0.1));
                border:1px solid rgba(124,58,237,0.4); border-radius:20px; padding:28px;
                text-align:center;'>
        <div style='font-size:3.5rem; margin-bottom:12px;'>{persona_data["icon"]}</div>
        <div style='font-family:Space Grotesk,sans-serif; font-weight:700; font-size:1.3rem;
                    color:#f8fafc; margin-bottom:6px;'>
            {persona or "Cultural"} Traveler</div>
        <div style='font-size:0.85rem; color:#94a3b8; line-height:1.5;'>{persona_data["desc"]}</div>
        <div style='margin-top:16px; padding:10px; background:rgba(124,58,237,0.15);
                    border-radius:10px;'>
            <div style='font-size:0.75rem; color:#94a3b8;'>Sessions</div>
            <div style='font-family:Space Grotesk,sans-serif; font-size:2rem;
                        font-weight:700; color:{persona_data["color"]};'>{SESSION_ID}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with p_col2:
    st.markdown("### 📊 Travel Stats")
    s1, s2, s3 = st.columns(3)
    with s1:
        st.metric("🌍 Trips Planned", trip_count)
    with s2:
        recent_score = result.get("travel_score", {}).get("total", 0) if result else 0
        st.metric("⭐ Last Score", f"{recent_score:.0f}" if recent_score else "—")
    with s3:
        last_dest = result.get("destination", "—") if result else "—"
        st.metric("📍 Last Destination", last_dest[:15] + ("..." if len(last_dest) > 15 else ""))

    if result:
        st.markdown("### ✨ Personalized Tips")
        tips = result.get("personalized_tips", [])
        for tip in tips[:4]:
            st.markdown(f"""<div class='tip-card'>💡 {tip}</div>""", unsafe_allow_html=True)
    else:
        st.info("Plan a trip first to receive personalized tips based on your travel persona.")

st.markdown("---")

# ─── Update Preferences ───────────────────────────────────────
st.markdown("### ⚙️ Update Travel Preferences")

with st.form("preferences_form"):
    fc1, fc2 = st.columns(2)
    with fc1:
        pref_name = st.text_input("Your Name", placeholder="Optional", key="pref_name")
        pref_style = st.selectbox("Travel Style",
                                   ["Any", "Relaxed", "Active", "Luxury", "Budget-Conscious", "Adventure"],
                                   key="pref_style")
        pref_climate = st.selectbox("Preferred Climate",
                                     ["Any", "Tropical", "Mediterranean", "Temperate", "Cold", "Desert"],
                                     key="pref_climate")
    with fc2:
        pref_email = st.text_input("Email (for reports)", placeholder="optional@email.com", key="pref_email")
        pref_accommodation = st.selectbox("Preferred Accommodation",
                                           ["Any", "Hotel", "Boutique Hotel", "Resort", "Hostel", "Villa"],
                                           key="pref_accommodation")
        pref_dietary = st.selectbox("Dietary Preference",
                                     ["None", "Vegetarian", "Vegan", "Halal", "Kosher", "Gluten-Free"],
                                     key="pref_dietary")

    pref_activities = st.multiselect(
        "Favourite Activities",
        ["Beaches", "Hiking", "Museums", "Food Tours", "Nightlife", "Shopping",
         "Yoga", "Adventure Sports", "Photography", "Architecture"],
        key="pref_activities",
    )

    save_prefs = st.form_submit_button("💾 Save Preferences", use_container_width=True)

if save_prefs:
    try:
        payload = {
            "name": pref_name or None,
            "email": pref_email or None,
            "travel_style": pref_style,
            "preferred_climate": pref_climate,
            "accommodation_type": pref_accommodation,
            "dietary": pref_dietary,
            "activities": pref_activities,
        }
        resp = requests.put(
            f"{BACKEND_URL}/api/users/{SESSION_ID}/preferences",
            json=payload,
            timeout=15,
        )
        if resp.status_code == 200:
            st.success("✅ Preferences saved! They'll be used to personalize your next trip.")
        else:
            st.error(f"Failed to save: {resp.text}")
    except requests.exceptions.ConnectionError:
        st.error("Cannot connect to backend.")

# ─── Trip History ─────────────────────────────────────────────
st.markdown("---")
st.markdown("### 🕒 Trip History")

try:
    resp = requests.get(f"{BACKEND_URL}/api/trips/user/{SESSION_ID}", timeout=10)
    if resp.status_code == 200:
        trips = resp.json()
        if trips:
            for t in trips:
                score = t.get("travel_score") or 0
                score_color = "#10b981" if score >= 70 else "#f5a623" if score >= 55 else "#e94560"
                st.markdown(f"""
                <div style='background:rgba(22,33,62,0.6); border:1px solid rgba(255,255,255,0.08);
                            border-radius:10px; padding:14px; margin-bottom:8px;
                            display:flex; justify-content:space-between; align-items:center;'>
                    <div>
                        <div style='font-weight:700; color:#f8fafc; margin-bottom:4px; display:flex; align-items:center; gap:8px;'>
                            🌍 {t.get("destination")}
                            <span style='background:rgba(16,185,129,0.15); color:#10b981; border:1px solid rgba(16,185,129,0.3); border-radius:12px; padding:2px 8px; font-size:0.65rem; font-weight:700; text-transform:uppercase;'>🤖 AI Recommended</span>
                        </div>
                        <div style='color:#64748b; font-size:0.8rem;'>
                            Budget: ${t.get("budget_usd", 0):,.0f}  |  Est: ${t.get("estimated_cost_usd", 0):,.0f}  |  {t.get("created_at", "")[:10]}
                        </div>
                    </div>
                    <div style='text-align:right;'>
                        <div style='font-weight:700; color:{score_color}; font-size:1.3rem;'>{score:.0f}</div>
                        <div style='font-size:0.7rem; color:#64748b;'>Travel Score</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No trip history yet. Plan your first trip!")
    else:
        st.info("Connect the backend to see trip history.")
except Exception:
    st.info("Trip history will appear here after connecting the backend.")
