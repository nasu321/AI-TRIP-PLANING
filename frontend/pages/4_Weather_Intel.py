"""
Page 4: Weather Intelligence
7-day forecast cards, suitability score, and packing checklist.
"""
import streamlit as st
import plotly.graph_objects as go
from pathlib import Path

st.set_page_config(page_title="Weather Intel | AI Travel", page_icon="🌤️", layout="wide")

css_path = Path(__file__).parent.parent / "assets" / "style.css"
if css_path.exists():
    with open(css_path, encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

st.markdown("""<style>
.stApp { background: linear-gradient(135deg, #0f0c29 0%, #1a1a2e 40%, #16213e 100%); color: #f8fafc; }
section[data-testid="stSidebar"] { background: linear-gradient(180deg, #0f0c29, #1a1a2e); }
h1,h2,h3 { color: #f8fafc; font-family: 'Space Grotesk', sans-serif; }
p, label { color: #cbd5e1; }
div[data-testid="stMetricValue"] { color: #0ea5e9 !important; font-size: 1.6rem !important; }
</style>""", unsafe_allow_html=True)

st.markdown("""
<div class='destination-hero'>
    <h1>🌤️ Weather Intelligence</h1>
    <p>7-day forecast with suitability scoring and smart packing recommendations</p>
</div>
""", unsafe_allow_html=True)

result = st.session_state.get("trip_result")
if not result:
    st.warning("⚠️ No trip planned yet. Go to **🗺️ Plan Trip** first.")
    st.stop()

weather = result.get("weather", {})
destination = result.get("destination", "")
forecast = weather.get("forecast", [])
suitability = weather.get("suitability_score", 0)
suitability_label = weather.get("suitability_label", "")
packing_tips = weather.get("packing_tips", [])
best_time_note = weather.get("best_time_note", "")

# ─── Suitability Header ───────────────────────────────────────
suit_color = "#10b981" if suitability >= 75 else "#f5a623" if suitability >= 55 else "#e94560"

m1, m2, m3 = st.columns(3)
with m1:
    st.metric("🌡️ Suitability Score", f"{suitability:.0f}/100")
with m2:
    st.metric("🏷️ Status", suitability_label)
with m3:
    avg_high = sum(d.get("temp_high_c", 0) for d in forecast) / max(len(forecast), 1)
    st.metric("🌡️ Avg High", f"{avg_high:.1f}°C")

st.markdown(f"""
<div class='info-banner'>
    📍 <strong>Best Time Note:</strong> {best_time_note}
</div>
""", unsafe_allow_html=True)

# ─── 7-Day Forecast Cards ─────────────────────────────────────
st.markdown("### 📅 7-Day Forecast")
if forecast:
    cols = st.columns(len(forecast))
    for i, day in enumerate(forecast):
        with cols[i]:
            cond = day.get("condition", "")
            icon = day.get("icon", "🌤️")
            t_high = day.get("temp_high_c", 0)
            t_low = day.get("temp_low_c", 0)
            humidity = day.get("humidity_pct", 0)
            precip = day.get("precipitation_mm", 0)
            wind = day.get("wind_kmh", 0)

            # Temp color gradient
            if t_high >= 30:
                temp_color = "#e94560"
            elif t_high >= 20:
                temp_color = "#f5a623"
            else:
                temp_color = "#0ea5e9"

            st.markdown(f"""
            <div class='weather-card'>
                <div class='weather-day'>{day.get("date", f"Day {i+1}")}</div>
                <div class='weather-icon' style='margin:8px 0;'>{icon}</div>
                <div class='weather-temp' style='color:{temp_color};'>{t_high:.0f}°</div>
                <div style='color:#64748b; font-size:0.75rem;'>{t_low:.0f}° low</div>
                <div style='font-size:0.72rem; color:#94a3b8; margin-top:6px; line-height:1.4;'>
                    💧{humidity}%<br>
                    🌧️{precip:.0f}mm<br>
                    🌬️{wind:.0f}km/h
                </div>
            </div>
            """, unsafe_allow_html=True)

# ─── Temperature Chart ────────────────────────────────────────
st.markdown("### 📈 Temperature Trend")
if forecast:
    days_labels = [d.get("date", f"Day {i+1}") for i, d in enumerate(forecast)]
    highs = [d.get("temp_high_c", 0) for d in forecast]
    lows = [d.get("temp_low_c", 0) for d in forecast]

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=days_labels, y=highs, name="High °C",
        line=dict(color="#e94560", width=3),
        fill=None, mode="lines+markers",
        marker=dict(size=8, color="#e94560"),
    ))
    fig.add_trace(go.Scatter(
        x=days_labels, y=lows, name="Low °C",
        line=dict(color="#0ea5e9", width=3),
        fill="tonexty",
        fillcolor="rgba(14,165,233,0.1)",
        mode="lines+markers",
        marker=dict(size=8, color="#0ea5e9"),
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(22,33,62,0.3)",
        font=dict(color="#94a3b8"),
        xaxis=dict(gridcolor="rgba(255,255,255,0.05)", tickfont=dict(color="#94a3b8")),
        yaxis=dict(gridcolor="rgba(255,255,255,0.05)", tickfont=dict(color="#94a3b8"),
                   ticksuffix="°C"),
        legend=dict(bgcolor="rgba(22,33,62,0.5)"),
        margin=dict(t=10, b=10, l=40, r=10),
        height=280,
    )
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# ─── Packing Checklist ────────────────────────────────────────
st.markdown("### 🎒 AI Packing Recommendations")
pack_col1, pack_col2 = st.columns(2)

packing_items = packing_tips if packing_tips else [
    "🕶️ Sunglasses and sunscreen", "👟 Comfortable walking shoes",
    "📱 Travel adapter for local outlets", "💊 First-aid kit and medications",
    "📄 Printed copies of bookings", "💳 Multiple payment methods",
]

half = len(packing_items) // 2
for i, item in enumerate(packing_items[:half]):
    with pack_col1:
        st.checkbox(item, value=False, key=f"pack_{i}")
for i, item in enumerate(packing_items[half:]):
    with pack_col2:
        st.checkbox(item, value=False, key=f"pack2_{i}")

# Humidity comfort guide
st.markdown("---")
st.markdown("### 💧 Weather Comfort Guide")
if forecast:
    avg_humidity = sum(d.get("humidity_pct", 0) for d in forecast) / len(forecast)
    avg_precip = sum(d.get("precipitation_mm", 0) for d in forecast) / len(forecast)

    if avg_humidity > 80:
        humidity_note = "🌊 High humidity expected — breathable, moisture-wicking clothing is essential."
    elif avg_humidity > 60:
        humidity_note = "💧 Moderate humidity — light layers work well."
    else:
        humidity_note = "☀️ Low humidity — comfortable conditions, stay hydrated."

    if avg_precip > 8:
        rain_note = "☂️ Significant rainfall expected — pack a waterproof jacket and umbrella."
    elif avg_precip > 3:
        rain_note = "🌦️ Some rain possible — a light rain jacket would be useful."
    else:
        rain_note = "🌞 Mostly dry conditions expected throughout your stay."

    st.markdown(f"""
    <div style='background:rgba(14,165,233,0.1); border:1px solid rgba(14,165,233,0.3);
                border-radius:12px; padding:16px; margin:8px 0;'>
        <div style='font-size:0.9rem; color:#f8fafc; margin-bottom:6px;'>{humidity_note}</div>
        <div style='font-size:0.9rem; color:#f8fafc;'>{rain_note}</div>
        <div style='font-size:0.8rem; color:#64748b; margin-top:8px;'>
            Avg Humidity: {avg_humidity:.0f}%  |  Avg Daily Precip: {avg_precip:.1f}mm
        </div>
    </div>
    """, unsafe_allow_html=True)
