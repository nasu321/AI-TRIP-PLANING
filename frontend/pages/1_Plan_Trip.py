"""
Page 1: Plan Trip — Main trip planning form and agent execution UI.
"""
import streamlit as st
import requests
import json
from datetime import date, timedelta
from pathlib import Path

# ─── Page Setup ──────────────────────────────────────────────
st.set_page_config(page_title="Plan Trip | AI Travel", page_icon="🗺️", layout="wide")

# Load CSS
css_path = Path(__file__).parent.parent / "assets" / "style.css"
if css_path.exists():
    with open(css_path, encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

st.markdown("""<style>
.stApp { background: linear-gradient(135deg, #0f0c29 0%, #1a1a2e 40%, #16213e 100%); color: #f8fafc; }
section[data-testid="stSidebar"] { background: linear-gradient(180deg, #0f0c29, #1a1a2e); }
.stButton > button { background: linear-gradient(135deg, #e94560, #f5a623); color: white;
    border: none; border-radius: 10px; font-weight: 600; padding: 12px 24px; width: 100%; }
.stButton > button:hover { transform: translateY(-2px); box-shadow: 0 8px 25px rgba(233,69,96,0.4); }
.stTextInput > div > div > input, .stNumberInput > div > div > input,
.stDateInput > div > div > input, .stSelectbox > div > div {
    background: rgba(22,33,62,0.8) !important; border: 1px solid rgba(255,255,255,0.15) !important;
    color: #f8fafc !important; border-radius: 10px !important; }
h1, h2, h3 { color: #f8fafc; font-family: 'Space Grotesk', sans-serif; }
p, label { color: #cbd5e1; }
div[data-testid="stMetricValue"] { color: #f5a623 !important; font-size: 1.6rem !important; }
</style>""", unsafe_allow_html=True)

# ─── Header ───────────────────────────────────────────────────
st.markdown("""
<div class='destination-hero'>
    <h1>🗺️ Plan Your Dream Trip</h1>
    <p>Tell our AI agents where you want to go — they'll handle the rest</p>
</div>
""", unsafe_allow_html=True)

BACKEND_URL = st.session_state.get("backend_url", "http://127.0.0.1:8000")
SESSION_ID = st.session_state.get("session_id", "demo")

# ─── Trip Planning Form ───────────────────────────────────────
with st.form("trip_plan_form", clear_on_submit=False):
    st.markdown("### 🌍 Destination & Dates")
    col1, col2 = st.columns(2)
    with col1:
        destination = st.text_input(
            "Destination City / Country",
            placeholder="e.g. Paris, France | Bali, Indonesia | Tokyo, Japan",
            key="dest_input",
        )
    with col2:
        travel_purpose = st.selectbox(
            "Travel Purpose",
            ["Leisure", "Honeymoon", "Adventure", "Business", "Family Vacation",
             "Solo Travel", "Cultural Exploration", "Relaxation"],
            key="purpose_select",
        )

    col3, col4 = st.columns(2)
    with col3:
        start_date = st.date_input("Departure Date", value=date.today() + timedelta(days=30), key="start_date")
    with col4:
        end_date = st.date_input("Return Date", value=date.today() + timedelta(days=37), key="end_date")

    st.markdown("### 💰 Budget & Travelers")
    col5, col6, col7 = st.columns(3)
    with col5:
        budget = st.number_input("Total Budget (USD)", min_value=500, max_value=100000,
                                  value=3000, step=100, key="budget_input")
    with col6:
        travelers = st.number_input("Number of Travelers", min_value=1, max_value=20,
                                     value=1, step=1, key="travelers_input")
    with col7:
        currency = st.selectbox("Currency", ["USD", "EUR", "GBP", "JPY", "AUD", "CAD",
                                              "SGD", "AED", "INR", "THB"], key="currency_select")

    st.markdown("### 🎯 Preferences")
    col8, col9, col10 = st.columns(3)
    with col8:
        accommodation = st.selectbox("Accommodation Type",
                                      ["Hotel", "Boutique Hotel", "Resort", "Hostel", "Airbnb", "Villa"],
                                      key="accomm_select")
    with col9:
        travel_style = st.selectbox("Travel Style",
                                     ["Relaxed", "Active", "Luxury", "Budget-Conscious", "Adventure", "Cultural"],
                                     key="style_select")
    with col10:
        climate_pref = st.selectbox("Preferred Climate",
                                     ["Any", "Tropical & Warm", "Mediterranean", "Temperate", "Cold & Snowy", "Desert"],
                                     key="climate_select")

    activities = st.multiselect(
        "Interests & Activities",
        ["Beaches", "Hiking & Nature", "Museums & History", "Local Food & Cuisine",
         "Nightlife", "Shopping", "Yoga & Wellness", "Adventure Sports",
         "Photography", "Architecture", "Wildlife", "Water Sports"],
        default=["Local Food & Cuisine", "Museums & History"],
        key="activities_select",
    )

    submitted = st.form_submit_button("🚀 Launch AI Agents & Plan My Trip", use_container_width=True)


# ─── Agent Execution ──────────────────────────────────────────
if submitted:
    if not destination:
        st.error("⚠️ Please enter a destination to continue.")
    elif start_date >= end_date:
        st.error("⚠️ Return date must be after departure date.")
    else:
        # Agent progress display
        st.markdown("---")
        st.markdown("### 🤖 AI Agents Working...")

        agent_cols = st.columns(6)
        agent_placeholders = []
        agent_info = [
            ("🌤️", "Weather"),
            ("🏨", "Hotels"),
            ("✈️", "Flights"),
            ("💬", "Reviews"),
            ("💰", "Budget"),
            ("🗓️", "Planner"),
        ]

        for i, (icon, name) in enumerate(agent_info):
            with agent_cols[i]:
                ph = st.empty()
                ph.markdown(f"""
                <div style='text-align:center; background:rgba(22,33,62,0.6);
                            border:1px solid rgba(255,255,255,0.1); border-radius:12px;
                            padding:16px; margin-bottom:8px;'>
                    <div style='font-size:1.8rem; animation: spin 2s linear infinite;'>{icon}</div>
                    <div style='color:#f5a623; font-size:0.8rem; font-weight:600; margin-top:4px;'>{name}</div>
                    <div style='color:#64748b; font-size:0.7rem;'>Running...</div>
                </div>
                """, unsafe_allow_html=True)
                agent_placeholders.append(ph)

        progress_bar = st.progress(0, text="Initializing agents...")

        # Build request payload
        payload = {
            "session_id": SESSION_ID,
            "destination": destination,
            "start_date": str(start_date),
            "end_date": str(end_date),
            "budget_usd": float(budget),
            "currency": currency,
            "travelers_count": int(travelers),
            "travel_purpose": travel_purpose,
            "preferences": {
                "accommodation_type": accommodation.lower(),
                "travel_style": travel_style.lower(),
                "preferred_climate": climate_pref.lower(),
                "activities": activities,
            },
        }

        try:
            # Simulate agent progress
            import time
            steps = [
                (20, "🌤️ Weather agent analyzing conditions..."),
                (40, "🏨 Recommendation agent scoring hotels..."),
                (55, "✈️ Flight agent searching routes..."),
                (70, "💬 Review agent processing sentiment..."),
                (85, "💰 Budget agent computing costs..."),
                (95, "🗓️ Planner agent building your itinerary..."),
            ]

            for pct, msg in steps:
                time.sleep(0.3)
                progress_bar.progress(pct, text=msg)

            # Auto-start backend if not running (failsafe for Streamlit Cloud)
            import socket
            import subprocess
            import sys
            import os
            def is_port_in_use(port):
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    return s.connect_ex(('127.0.0.1', port)) == 0

            if not is_port_in_use(8000):
                progress_bar.progress(98, text="🚀 Starting backend server on cloud...")
                backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'backend'))
                sys.path.append(backend_path)
                
                log_file = os.path.join(backend_path, "backend_cloud.log")
                with open(log_file, "w") as log_f:
                    subprocess.Popen(
                        [sys.executable, "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8000"],
                        cwd=backend_path,
                        stdout=log_f,
                        stderr=subprocess.STDOUT
                    )
                import time
                time.sleep(5) # Wait for backend to fully boot
                
                if not is_port_in_use(8000):
                    # It failed to start! Let's read the log and show it to the user.
                    try:
                        with open(log_file, "r") as f:
                            error_log = f.read()
                        st.error(f"Backend failed to start on cloud! Error Log:\n\n```text\n{error_log}\n```")
                    except Exception as e:
                        st.error("Backend failed to start on cloud, and log file could not be read.")
            
            # Make API call
            with st.spinner(""):
                try:
                    response = requests.post(
                        f"{BACKEND_URL}/api/trips/plan",
                        json=payload,
                        timeout=120,
                    )
                except requests.exceptions.ConnectionError:
                    response = None

            progress_bar.progress(100, text="✅ All agents complete!")

            if response and response.status_code == 200:
                result = response.json()
                st.session_state.trip_result = result
                st.session_state.trip_destination = destination

                # Update agent status cards to complete
                for i, (icon, name) in enumerate(agent_info):
                    agent_placeholders[i].markdown(f"""
                    <div style='text-align:center; background:rgba(16,185,129,0.1);
                                border:1px solid rgba(16,185,129,0.4); border-radius:12px;
                                padding:16px; margin-bottom:8px;'>
                        <div style='font-size:1.8rem;'>{icon}</div>
                        <div style='color:#10b981; font-size:0.8rem; font-weight:600; margin-top:4px;'>{name}</div>
                        <div style='color:#10b981; font-size:0.7rem;'>✅ Done</div>
                    </div>
                    """, unsafe_allow_html=True)

                # ── Results Display ──────────────────────────────
                travel_score = result.get("travel_score", {})
                score_total = travel_score.get("total", 0)
                score_label = travel_score.get("label", "")

                st.markdown(f"""
                <div class='score-hero'>
                    <div style='color:#94a3b8; font-size:0.9rem; text-transform:uppercase;
                                letter-spacing:0.1em; margin-bottom:8px;'>TRAVEL SCORE</div>
                    <div class='score-number'>{score_total:.0f}</div>
                    <div class='score-label'>{score_label}</div>
                    <div style='color:#64748b; font-size:0.85rem; margin-top:12px;'>
                        {travel_score.get("explanation", "")}
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # Score breakdown
                sc1, sc2, sc3, sc4, sc5 = st.columns(5)
                score_dims = [
                    (sc1, "🌤️ Weather", travel_score.get("weather_score", 0)),
                    (sc2, "💰 Budget", travel_score.get("budget_score", 0)),
                    (sc3, "🏨 Hotels", travel_score.get("hotel_score", 0)),
                    (sc4, "💬 Sentiment", travel_score.get("sentiment_score", 0)),
                    (sc5, "✈️ Flights", travel_score.get("flight_score", 0)),
                ]
                for col, label, score in score_dims:
                    with col:
                        color = "#10b981" if score >= 70 else "#f5a623" if score >= 55 else "#e94560"
                        st.markdown(f"""
                        <div style='text-align:center; background:rgba(22,33,62,0.7);
                                    border-radius:12px; padding:14px; border:1px solid rgba(255,255,255,0.08);'>
                            <div style='font-size:0.8rem; color:#94a3b8;'>{label}</div>
                            <div style='font-size:1.8rem; font-weight:700; color:{color};
                                        font-family:Space Grotesk,sans-serif;'>{score:.0f}</div>
                            <div style='font-size:0.7rem; color:#64748b;'>/100</div>
                        </div>
                        """, unsafe_allow_html=True)

                st.success("✅ Trip plan ready! Navigate to the pages below to explore your results.")

                # Quick links
                st.markdown("""
                <div class='info-banner'>
                    <strong>📍 Explore your results:</strong>
                    Use the sidebar to navigate to
                    <strong>🏨 Recommendations</strong>,
                    <strong>📊 Budget Analytics</strong>,
                    <strong>🌤️ Weather Intel</strong>,
                    <strong>✈️ Flight Intel</strong>,
                    <strong>📄 Reports</strong>, and
                    <strong>👤 My Profile</strong>.
                </div>
                """, unsafe_allow_html=True)

            elif response:
                st.error(f"❌ API Error {response.status_code}: {response.text}")
            else:
                st.error("❌ Cannot connect to backend. The backend auto-launcher failed or is still starting up.")

        except requests.exceptions.ConnectionError:
            st.error(
                "❌ Cannot connect to backend. Make sure the FastAPI server is running:\n\n"
                "`cd backend && uvicorn app.main:app --reload --port 8000`"
            )
        except Exception as e:
            st.error(f"❌ Unexpected error: {str(e)}")

# ─── Show existing result if available ───────────────────────
elif st.session_state.get("trip_result"):
    result = st.session_state.trip_result
    travel_score = result.get("travel_score", {})
    score_total = travel_score.get("total", 0)

    st.info(f"📋 Previous trip plan loaded: **{result.get('destination')}** — Score: **{score_total:.0f}/100**")
    st.markdown("Navigate using the sidebar to explore your travel plan.")
