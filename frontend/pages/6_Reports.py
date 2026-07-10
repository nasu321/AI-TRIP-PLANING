"""
Page 6: PDF Reports & WhatsApp Delivery
"""
import streamlit as st
import requests
from pathlib import Path

st.set_page_config(page_title="Reports | AI Travel", page_icon="📄", layout="wide")

css_path = Path(__file__).parent.parent / "assets" / "style.css"
if css_path.exists():
    with open(css_path, encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

st.markdown("""<style>
.stApp { background: linear-gradient(135deg, #0f0c29 0%, #1a1a2e 40%, #16213e 100%); color: #f8fafc; }
section[data-testid="stSidebar"] { background: linear-gradient(180deg, #0f0c29, #1a1a2e); }
h1,h2,h3 { color: #f8fafc; font-family: 'Space Grotesk', sans-serif; }
p, label { color: #cbd5e1; }
.stButton > button { background: linear-gradient(135deg, #e94560, #f5a623); color: white;
    border: none; border-radius: 10px; font-weight: 600; padding: 12px 24px; width: 100%; }
.stButton > button:hover { transform: translateY(-2px); box-shadow: 0 8px 25px rgba(233,69,96,0.4); }
.stTextInput > div > div > input { background: rgba(22,33,62,0.8) !important;
    border: 1px solid rgba(255,255,255,0.15) !important; color: #f8fafc !important; border-radius: 10px !important; }
</style>""", unsafe_allow_html=True)

st.markdown("""
<div class='destination-hero'>
    <h1>📄 Travel Reports</h1>
    <p>Generate your professional PDF travel report and deliver it via WhatsApp</p>
</div>
""", unsafe_allow_html=True)

result = st.session_state.get("trip_result")
BACKEND_URL = st.session_state.get("backend_url", "http://127.0.0.1:8000")
SESSION_ID = st.session_state.get("session_id", "demo")

if not result:
    st.warning("⚠️ No trip planned yet. Go to **🗺️ Plan Trip** first.")
    st.stop()

trip_id = result.get("trip_id")
destination = result.get("destination", "")
travel_score = result.get("travel_score", {}).get("total", 0)

# ─── Report Overview ──────────────────────────────────────────
st.markdown(f"""
<div style='background:rgba(22,33,62,0.7); border:1px solid rgba(255,255,255,0.1);
            border-radius:16px; padding:24px; margin-bottom:24px;'>
    <div style='font-size:1.1rem; font-weight:700; color:#f8fafc; margin-bottom:12px;'>
        📋 Report Contents</div>
    <div style='display:grid; grid-template-columns:1fr 1fr; gap:12px;'>
        {"".join([
            f'''<div style="color:#94a3b8; font-size:0.85rem; padding:8px;
                          background:rgba(255,255,255,0.04); border-radius:6px;">✅ {item}</div>'''
            for item in [
                "Destination Overview & AI Summary", "Travel Score Breakdown (5 dimensions)",
                "7-Day Weather Forecast & Packing Tips", "Top Hotel Recommendations with Scores",
                "Flight Options & Price Analysis", "Detailed Budget Breakdown",
                "Day-by-Day Itinerary", "Review Intelligence & Sentiment Analysis",
                "Local Attractions Guide", "Personalized Travel Tips",
            ]
        ])}
    </div>
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns(2)

# ─── PDF Generation ───────────────────────────────────────────
with col1:
    st.markdown("### 📥 Generate PDF Report")

    if st.button("📄 Generate Professional PDF Report"):
        with st.spinner("Creating your PDF report..."):
            try:
                resp = requests.post(
                    f"{BACKEND_URL}/api/reports/generate",
                    json={"trip_id": trip_id, "session_id": SESSION_ID},
                    timeout=60,
                )
                if resp.status_code == 200:
                    report_data = resp.json()
                    st.session_state.report_id = report_data.get("report_id")
                    st.session_state.report_filename = report_data.get("pdf_filename")
                    st.success(f"✅ PDF Report Generated: **{report_data.get('pdf_filename')}**")

                    # Download button
                    download_url = f"{BACKEND_URL}{report_data.get('download_url', '')}"
                    try:
                        dl_resp = requests.get(download_url, timeout=30)
                        if dl_resp.status_code == 200:
                            st.download_button(
                                label="⬇️ Download PDF Report",
                                data=dl_resp.content,
                                file_name=report_data.get("pdf_filename", "travel_report.pdf"),
                                mime="application/pdf",
                            )
                    except Exception:
                        st.info(f"Download URL: {download_url}")
                else:
                    st.error(f"PDF generation failed: {resp.text}")
            except requests.exceptions.ConnectionError:
                st.error("Cannot connect to backend. Make sure the server is running.")

    # Report metadata
    if st.session_state.get("report_id"):
        st.markdown(f"""
        <div style='background:rgba(16,185,129,0.1); border:1px solid rgba(16,185,129,0.3);
                    border-radius:10px; padding:14px; margin-top:12px;'>
            <div style='color:#10b981; font-size:0.85rem;'>✅ Report Ready</div>
            <div style='color:#94a3b8; font-size:0.8rem;'>ID: {st.session_state.report_id}</div>
            <div style='color:#94a3b8; font-size:0.8rem;'>{st.session_state.get("report_filename", "")}</div>
        </div>
        """, unsafe_allow_html=True)

# ─── WhatsApp Delivery ────────────────────────────────────────
with col2:
    st.markdown("### 📱 Send via WhatsApp")

    st.markdown(f"""
    <div class='info-banner'>
        📤 Send your travel report directly to WhatsApp.<br>
        <small>Requires Twilio configuration. In demo mode, delivery is simulated.</small>
    </div>
    """, unsafe_allow_html=True)

    phone_number = st.text_input(
        "WhatsApp Phone Number",
        placeholder="+1234567890 (include country code)",
        key="wa_phone",
    )
    custom_msg = st.text_area(
        "Custom Message (optional)",
        placeholder="Add a personal note to your travel report...",
        height=80,
        key="wa_msg",
    )

    if st.button("📲 Send Report via WhatsApp"):
        if not phone_number:
            st.error("Please enter a valid phone number.")
        else:
            with st.spinner("Sending WhatsApp message..."):
                try:
                    resp = requests.post(
                        f"{BACKEND_URL}/api/reports/send-whatsapp",
                        json={
                            "trip_id": trip_id,
                            "session_id": SESSION_ID,
                            "phone_number": phone_number,
                            "custom_message": custom_msg or None,
                        },
                        timeout=30,
                    )
                    if resp.status_code == 200:
                        wa_data = resp.json()
                        st.success(f"✅ WhatsApp message sent to {phone_number}!")
                        extra = wa_data.get("data", {})
                        if extra.get("note"):
                            st.info(f"ℹ️ {extra['note']}")
                    else:
                        st.error(f"WhatsApp failed: {resp.text}")
                except requests.exceptions.ConnectionError:
                    st.error("Cannot connect to backend.")

st.markdown("---")

# ─── Report Preview (Trip Summary) ───────────────────────────
st.markdown("### 👁️ Report Preview")

tabs = st.tabs(["📋 Summary", "🗓️ Itinerary", "💬 Review Intelligence"])

with tabs[0]:
    ts = result.get("travel_score", {})
    st.markdown(f"""
    <div style='background:rgba(22,33,62,0.7); border-radius:12px; padding:20px;'>
        <h3 style='color:#f5a623; margin:0 0 12px 0;'>🌍 {destination}</h3>
        <div style='color:#94a3b8; font-size:0.9rem; line-height:1.6;'>
            {result.get("agent_reasoning", "AI analysis complete.")[:600]}...
        </div>
        <div style='margin-top:16px; display:flex; gap:20px; flex-wrap:wrap;'>
            <div style='text-align:center;'>
                <div style='font-size:2rem; font-weight:800; color:#f5a623;'>{ts.get("total", 0):.0f}</div>
                <div style='font-size:0.75rem; color:#64748b;'>Travel Score</div>
            </div>
            <div style='text-align:center;'>
                <div style='font-size:2rem; font-weight:800; color:#0ea5e9;'>{ts.get("weather_score", 0):.0f}</div>
                <div style='font-size:0.75rem; color:#64748b;'>Weather</div>
            </div>
            <div style='text-align:center;'>
                <div style='font-size:2rem; font-weight:800; color:#10b981;'>{ts.get("budget_score", 0):.0f}</div>
                <div style='font-size:0.75rem; color:#64748b;'>Budget Fit</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with tabs[1]:
    itinerary = result.get("itinerary", [])
    for day in itinerary[:5]:
        st.markdown(f"""
        <div class='itinerary-day'>
            <div class='itinerary-day-header'>Day {day.get("day_number")}: {day.get("title")}</div>
            <div style='color:#94a3b8; font-size:0.85rem;'>
                🎯 {" | ".join(day.get("activities", [])[:3])}</div>
            <div style='color:#64748b; font-size:0.8rem; margin-top:4px;'>
                🍽️ {" | ".join(day.get("meals", []))}  |  🏨 {day.get("accommodation", "")}
                |  💰 ~${day.get("estimated_daily_cost_usd", 0):.0f}/day
            </div>
        </div>
        """, unsafe_allow_html=True)

with tabs[2]:
    reviews = result.get("review_insights", [])
    for review in reviews[:3]:
        pos = review.get("positive_pct", 0)
        neg = review.get("negative_pct", 0)
        st.markdown(f"""
        <div style='background:rgba(22,33,62,0.6); border-radius:12px; padding:16px; margin-bottom:12px;'>
            <div style='font-weight:700; color:#f8fafc;'>📍 {review.get("hotel_name")}</div>
            <div style='margin:8px 0; display:flex; gap:16px;'>
                <span class='sentiment-positive'>👍 {pos:.0f}% Positive</span>
                <span class='sentiment-negative'>👎 {neg:.0f}% Negative</span>
                <span style='color:#94a3b8;'>📊 {review.get("total_reviews", 0):,} reviews</span>
            </div>
            <div style='color:#94a3b8; font-size:0.85rem; font-style:italic;'>
                {review.get("ai_summary", "")}</div>
            <div style='margin-top:8px;'>
                <span style='color:#10b981; font-size:0.8rem;'>
                    Pros: {" • ".join(review.get("top_pros", [])[:2])}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
