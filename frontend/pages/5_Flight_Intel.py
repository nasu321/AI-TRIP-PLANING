"""
Page 5: Flight Intelligence
Flight options, price comparison, and cheapest window highlight.
"""
import streamlit as st
import plotly.graph_objects as go
from pathlib import Path

st.set_page_config(page_title="Flight Intel | AI Travel", page_icon="✈️", layout="wide")

css_path = Path(__file__).parent.parent / "assets" / "style.css"
if css_path.exists():
    with open(css_path, encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

st.markdown("""<style>
.stApp { background: linear-gradient(135deg, #0f0c29 0%, #1a1a2e 40%, #16213e 100%); color: #f8fafc; }
section[data-testid="stSidebar"] { background: linear-gradient(180deg, #0f0c29, #1a1a2e); }
h1,h2,h3 { color: #f8fafc; font-family: 'Space Grotesk', sans-serif; }
p, label { color: #cbd5e1; }
div[data-testid="stMetricValue"] { color: #f5a623 !important; font-size: 1.6rem !important; }
</style>""", unsafe_allow_html=True)

st.markdown("""
<div class='destination-hero'>
    <h1>✈️ Flight Intelligence</h1>
    <p>AI-curated flight options with affordability scoring and cost insights</p>
</div>
""", unsafe_allow_html=True)

result = st.session_state.get("trip_result")
if not result:
    st.warning("⚠️ No trip planned yet. Go to **🗺️ Plan Trip** first.")
    st.stop()

flights = result.get("flights", [])
destination = result.get("destination", "")

if not flights:
    st.info("No flight data available.")
    st.stop()

# ─── Key Metrics ──────────────────────────────────────────────
cheapest = min(flights, key=lambda f: f.get("price_usd", 9999))
priciest = max(flights, key=lambda f: f.get("price_usd", 0))
avg_price = sum(f.get("price_usd", 0) for f in flights) / len(flights)
avg_duration = sum(f.get("duration_hours", 0) for f in flights) / len(flights)

m1, m2, m3, m4 = st.columns(4)
with m1:
    st.metric("💸 Best Price", f"${cheapest.get('price_usd', 0):,.0f}", delta=f"{cheapest.get('airline', '')}")
with m2:
    st.metric("📊 Avg Price", f"${avg_price:,.0f}")
with m3:
    st.metric("⏱️ Avg Duration", f"{avg_duration:.1f}h")
with m4:
    direct_count = sum(1 for f in flights if f.get("stops", 0) == 0)
    st.metric("🛫 Direct Flights", f"{direct_count}/{len(flights)}")

st.markdown("---")

# ─── Flight Cards ─────────────────────────────────────────────
st.markdown("### 🎟️ Available Flights")

# Sort options
sort_opt = st.radio("Sort by:", ["Best Price", "Fastest", "Best Score"], horizontal=True)
sort_funcs = {
    "Best Price": lambda f: f.get("price_usd", 9999),
    "Fastest": lambda f: f.get("duration_hours", 99),
    "Best Score": lambda f: -f.get("affordability_score", 0),
}
sorted_flights = sorted(flights, key=sort_funcs[sort_opt])

for fi, flight in enumerate(sorted_flights):
    is_cheapest = flight.get("is_cheapest", False)
    is_fastest = flight.get("is_fastest", False)
    price = flight.get("price_usd", 0)
    airline = flight.get("airline", "")
    duration = flight.get("duration_hours", 0)
    stops = flight.get("stops", 0)
    dep = flight.get("departure_time", "")
    arr = flight.get("arrival_time", "")
    affscore = flight.get("affordability_score", 0)

    border_color = "#10b981" if is_cheapest else "#3b82f6" if is_fastest else "#1e293b"
    score_color = "#10b981" if affscore >= 70 else "#f5a623" if affscore >= 50 else "#e94560"
    stops_label = "Direct 🟢" if stops == 0 else f"{stops} stop{'s' if stops > 1 else ''} 🟡"

    st.markdown(f"""
    <div class='flight-card {"cheapest" if is_cheapest else ""}' style='border-color:{border_color};'>
        <div style='flex:2;'>
            <div style='font-weight:700; font-size:1.0rem; color:#f8fafc;'>
                {'💸 BEST PRICE - ' if is_cheapest else ''}{'⚡ FASTEST - ' if is_fastest else ''}✈️ {airline}</div>
            <div style='color:#64748b; font-size:0.8rem; margin-top:4px;'>
                {flight.get("flight_number", "")} &nbsp;|&nbsp; {stops_label}
            </div>
            <div style='color:#94a3b8; font-size:0.8rem; margin-top:4px;'>
                📍 {flight.get("origin", "")} → {flight.get("destination", "")}
            </div>
        </div>
        <div style='flex:1; text-align:center;'>
            <div style='color:#94a3b8; font-size:0.75rem;'>DEPARTS</div>
            <div style='font-weight:700; color:#f8fafc; font-size:1.1rem;'>{dep}</div>
        </div>
        <div style='flex:1; text-align:center;'>
            <div style='color:#94a3b8; font-size:0.75rem;'>⏱️ {duration:.1f}h</div>
            <div style='color:#64748b; font-size:1.3rem;'>→</div>
        </div>
        <div style='flex:1; text-align:center;'>
            <div style='color:#94a3b8; font-size:0.75rem;'>ARRIVES</div>
            <div style='font-weight:700; color:#f8fafc; font-size:1.1rem;'>{arr}</div>
        </div>
        <div style='flex:1; text-align:center;'>
            <div class='flight-price'>${price:,.0f}</div>
            <div style='color:#64748b; font-size:0.75rem;'>per person</div>
        </div>
        <div style='flex:1; text-align:center; display:flex; flex-direction:column; justify-content:center; gap:6px;'>
            <div>
                <div style='font-size:0.7rem; color:#94a3b8;'>Affordability</div>
                <div style='font-weight:700; color:{score_color}; font-size:1.1rem;'>{affscore:.0f}/100</div>
            </div>
            <a href='https://www.google.com/travel/flights/search?q=flights+to+{destination.replace(" ", "+")}+on+{airline.replace(" ", "+")}' target='_blank' style='background:linear-gradient(135deg,#e94560,#f5a623); color:white; text-decoration:none; padding:6px 10px; border-radius:6px; font-size:0.75rem; font-weight:700; display:inline-block;'>Book Now</a>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ─── Price Comparison Chart ───────────────────────────────────
st.markdown("---")
st.markdown("### 📊 Price Comparison")

airlines = [f.get("airline", f"Flight {i+1}") for i, f in enumerate(sorted_flights)]
prices = [f.get("price_usd", 0) for f in sorted_flights]
colors = ["#10b981" if f.get("is_cheapest") else "#0ea5e9" for f in sorted_flights]

fig = go.Figure(data=[go.Bar(
    x=airlines, y=prices,
    marker=dict(color=colors, line=dict(color="#1a1a2e", width=1)),
    text=[f"${p:,.0f}" for p in prices],
    textposition="outside",
    textfont=dict(color="#f8fafc", size=10),
)])
fig.update_layout(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(22,33,62,0.3)",
    font=dict(color="#94a3b8"),
    xaxis=dict(tickfont=dict(color="#94a3b8"), gridcolor="rgba(255,255,255,0.05)"),
    yaxis=dict(tickfont=dict(color="#94a3b8"), gridcolor="rgba(255,255,255,0.05)", tickprefix="$"),
    margin=dict(t=40, b=10, l=40, r=10),
    height=280,
    annotations=[dict(
        text="🟢 Best Price", x=0, y=1.05, xref="paper", yref="paper",
        showarrow=False, font=dict(color="#10b981", size=11)
    )],
)
st.plotly_chart(fig, use_container_width=True)

# ─── Booking Tips ─────────────────────────────────────────────
st.markdown("---")
st.markdown("### 💡 Flight Booking Intelligence")
booking_tips = [
    "📅 Book 6-8 weeks in advance for domestic and 3-6 months for international flights",
    "📆 Tuesdays and Wednesdays typically offer 10-20% cheaper fares",
    "🔄 Consider one-stop flights — they're often 15-30% cheaper and some layovers are enjoyable",
    "🌅 Red-eye flights often offer lowest prices and arrive early for maximum exploration time",
    "💳 Use airline miles or credit card travel points for additional savings",
]
for tip in booking_tips:
    st.markdown(f"""<div class='tip-card'>{tip}</div>""", unsafe_allow_html=True)
