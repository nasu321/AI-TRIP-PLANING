"""
Page 8: Trip Output — Tourist Places, Nearby Services, Word Cloud, Day Schedule, Weather Impact, PDF.
"""
import io
import streamlit as st
import requests
import plotly.graph_objects as go
import plotly.express as px
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from pathlib import Path
from collections import Counter

st.set_page_config(page_title="Trip Output | AI Travel", page_icon="🗓️", layout="wide")

# ── CSS ──────────────────────────────────────────────────────────────────────
css_path = Path(__file__).parent.parent / "assets" / "style.css"
if css_path.exists():
    with open(css_path, encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&family=Space+Grotesk:wght@500;700&display=swap');
.stApp{background:linear-gradient(135deg,#0f0c29 0%,#1a1a2e 40%,#16213e 100%);color:#f8fafc;}
section[data-testid="stSidebar"]{background:linear-gradient(180deg,#0f0c29,#1a1a2e);}
h1,h2,h3{color:#f8fafc;font-family:'Space Grotesk',sans-serif;}
p,label,span{color:#cbd5e1;}
.stButton>button{background:linear-gradient(135deg,#e94560,#f5a623);color:white;
  border:none;border-radius:10px;font-weight:600;padding:12px 24px;width:100%;}
.stButton>button:hover{transform:translateY(-2px);box-shadow:0 8px 25px rgba(233,69,96,0.4);}
.stExpander{background:rgba(22,33,62,0.6);border-radius:12px;border:1px solid rgba(255,255,255,0.08);}
</style>""", unsafe_allow_html=True)

BACKEND_URL = st.session_state.get("backend_url", "http://127.0.0.1:8000")
SESSION_ID  = st.session_state.get("session_id", "demo")

# ── Section header helper ─────────────────────────────────────────────────────
def sec(icon, title):
    st.markdown(f"""
    <div style='display:flex;align-items:center;gap:12px;padding-bottom:12px;
                border-bottom:2px solid #e94560;margin:28px 0 20px 0;'>
        <span style='font-size:1.8rem;'>{icon}</span>
        <h2 style='margin:0;font-size:1.5rem;'>{title}</h2>
    </div>""", unsafe_allow_html=True)

def weather_color(precip, temp_high):
    if precip > 10: return "#60a5fa", "Rainy"
    if temp_high > 35: return "#f87171", "Very Hot"
    if temp_high > 28: return "#fb923c", "Warm"
    if temp_high > 18: return "#34d399", "Pleasant"
    return "#93c5fd", "Cool"

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div style='text-align:center;padding:30px 0 10px;'>
  <h1 style='font-size:2.4rem;background:linear-gradient(135deg,#e94560,#f5a623);
             -webkit-background-clip:text;-webkit-text-fill-color:transparent;margin-bottom:4px;'>
    🗓️ Your Complete Trip Output</h1>
  <p style='color:#94a3b8;font-size:1rem;'>Tourist Places · Nearby Services · Day Schedule · Weather Impact · PDF</p>
</div>""", unsafe_allow_html=True)

result = st.session_state.get("trip_result")
if not result:
    st.warning("⚠️ No trip planned yet. Go to **🗺️ Plan Trip** first.")
    st.stop()

destination  = result.get("destination", "")
itinerary    = result.get("itinerary", [])
attractions  = result.get("attractions", [])
services     = result.get("nearby_services", [])
weather      = result.get("weather", {})
forecast     = weather.get("forecast", [])
hotels       = result.get("recommended_hotels", [])
travel_score = result.get("travel_score", {})
budget       = result.get("budget", {})
trip_id      = result.get("trip_id")
tips         = result.get("personalized_tips", [])

# ════════════════════════════════════════════════════════════════════════════
# METRICS BAR
# ════════════════════════════════════════════════════════════════════════════
m1,m2,m3,m4,m5,m6 = st.columns(6)
def metric_card(col, label, value, sub, color):
    col.markdown(f"""
    <div style='text-align:center;background:rgba(22,33,62,0.8);border:1px solid {color}44;
                border-top:3px solid {color};border-radius:14px;padding:14px 6px;'>
        <div style='font-size:0.65rem;color:#94a3b8;text-transform:uppercase;letter-spacing:.08em;'>{label}</div>
        <div style='font-family:Space Grotesk,sans-serif;font-size:2rem;font-weight:800;color:{color};line-height:1.1;'>{value}</div>
        <div style='font-size:0.68rem;color:#64748b;margin-top:2px;'>{sub}</div>
    </div>""", unsafe_allow_html=True)

sc = travel_score.get("total", 0)
col_sc = "#10b981" if sc >= 75 else "#f5a623" if sc >= 55 else "#e94560"
metric_card(m1, "Travel Score", f"{sc:.0f}", travel_score.get("label","")[:12], col_sc)
metric_card(m2, "Weather", f"{weather.get('suitability_score',0):.0f}", weather.get("suitability_label","")[:14], "#0ea5e9")
city_rating = result.get("city_rating", 0.0)
col_cr = "#7c3aed" if city_rating >= 8.5 else "#f5a623"
metric_card(m3, "City Rating", f"{city_rating}/10", "Overall Vibe", col_cr)
metric_card(m4, "Nearby Services", str(len(services)), "Restaurants · ATMs · More", "#f5a623")
metric_card(m5, "Trip Days", str(len(itinerary)), "Scheduled", "#06b6d4")
metric_card(m6, "Est. Cost", f"${budget.get('total_estimated_usd',0):,.0f}", budget.get("budget_fit_label","")[:16], "#10b981")

# ════════════════════════════════════════════════════════════════════════════
# SECTION 1 — WORD CLOUD
# ════════════════════════════════════════════════════════════════════════════
sec("☁️", f"Places & Services Word Cloud — {destination}")

# Build word frequency corpus
word_freq = Counter()
cat_colors_map = {
    "Landmark":"#f5a623","Museum":"#7c3aed","Nature":"#10b981","Historical":"#e94560",
    "Cultural":"#0ea5e9","Adventure":"#fb923c","Spiritual":"#8b5cf6","Food & Culture":"#06b6d4",
}
for attr in attractions:
    name_words = attr.get("name","").split()
    for w in name_words:
        if len(w) > 2:
            word_freq[w] += 20
    for tag in attr.get("tags", []):
        for w in tag.split():
            if len(w) > 2:
                word_freq[w] += 12
    word_freq[attr.get("category","")] += 15

for svc in services:
    name_words = svc.get("name","").split()
    for w in name_words:
        if len(w) > 2:
            word_freq[w] += 10
    for tag in svc.get("tags", []):
        for w in tag.split():
            if len(w) > 2:
                word_freq[w] += 8
    stype = svc.get("service_type","").replace("_"," ").title()
    word_freq[stype] += 10

for h in hotels:
    for am in h.get("amenities", []):
        word_freq[am] += 6

# Destination name words get highest weight
for w in destination.split(",")[0].split():
    if len(w) > 2:
        word_freq[w] += 40

# Remove common stop words
stop = {"The","And","Of","In","With","For","A","An","Is","At","To","On","By"}
word_freq = {w: f for w,f in word_freq.items() if w not in stop and len(w) > 2}

try:
    from wordcloud import WordCloud

    # Build a custom color function using category colors
    base_colors = ["#e94560","#f5a623","#7c3aed","#0ea5e9","#10b981","#fb923c","#06b6d4","#8b5cf6","#f472b6","#34d399"]
    def color_func(word, font_size, position, orientation, random_state=None, **kwargs):
        import random
        return base_colors[hash(word) % len(base_colors)]

    wc = WordCloud(
        width=1400, height=500,
        background_color="#0f0c29",
        max_words=80,
        prefer_horizontal=0.7,
        min_font_size=12,
        max_font_size=90,
        collocations=False,
        color_func=color_func,
    ).generate_from_frequencies(word_freq)

    fig_wc, ax_wc = plt.subplots(figsize=(14, 5))
    ax_wc.imshow(wc, interpolation="bilinear")
    ax_wc.axis("off")
    fig_wc.patch.set_facecolor("#0f0c29")
    st.pyplot(fig_wc, use_container_width=True)
    plt.close(fig_wc)

except ImportError:
    # Fallback: tag cloud using plotly
    st.info("wordcloud library not found — showing tag cloud instead.")
    words  = list(word_freq.keys())[:50]
    counts = [word_freq[w] for w in words]
    cols_wc = ["#e94560","#f5a623","#7c3aed","#0ea5e9","#10b981","#fb923c","#8b5cf6","#06b6d4"]
    clr = [cols_wc[i % len(cols_wc)] for i in range(len(words))]
    tags_html = "".join([
        f"<span style='background:{c}22;color:{c};border:1px solid {c}44;border-radius:20px;"
        f"padding:4px 12px;margin:4px;display:inline-block;font-size:{max(0.7, min(1.4, 0.7+v/40)):.1f}rem;"
        f"font-weight:600;'>{w}</span>"
        for w,(c,v) in zip(words, zip(clr, counts))
    ])
    st.markdown(f"<div style='text-align:center;line-height:2.2;'>{tags_html}</div>", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
# SECTION 2 — TOURIST PLACES
# ════════════════════════════════════════════════════════════════════════════
sec("🗺️", f"Tourist Places & Attractions — {destination}")

if not attractions:
    st.info("No attraction data yet — plan a trip first.")
else:
    # We will use the same image card styling from Recommendations!
    st.markdown("""
    <style>
    .grid-container {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
        gap: 20px;
        padding: 10px 0;
    }
    .image-card {
        background: #1e293b;
        border-radius: 16px;
        border: 1px solid rgba(255,255,255,0.05);
        overflow: hidden;
        display: flex;
        flex-direction: column;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
    }
    .card-image-container {
        position: relative;
        height: 180px;
        width: 100%;
    }
    .card-image-container img {
        width: 100%;
        height: 100%;
        object-fit: cover;
    }
    .card-badge {
        position: absolute;
        top: 12px;
        left: 12px;
        background: white;
        color: #0f0c29;
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 700;
    }
    .card-content {
        padding: 16px;
        flex-grow: 1;
        display: flex;
        flex-direction: column;
    }
    .card-title-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 8px;
    }
    .card-title {
        font-size: 1.1rem;
        font-weight: 700;
        color: #f8fafc;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        max-width: 70%;
    }
    .card-price {
        font-size: 0.95rem;
        font-weight: 700;
        color: #94a3b8;
    }
    .card-tags {
        margin-bottom: 16px;
    }
    .card-tag {
        font-size: 0.65rem;
        background: rgba(255,255,255,0.1);
        color: #cbd5e1;
        padding: 4px 8px;
        border-radius: 6px;
        margin-right: 6px;
        text-transform: uppercase;
        font-weight: 600;
    }
    .card-ai-reasoning {
        background: rgba(16, 185, 129, 0.05);
        border-top: 1px solid rgba(16, 185, 129, 0.2);
        padding: 12px;
        margin-top: auto;
    }
    .card-ai-reasoning-title {
        font-size: 0.7rem;
        color: #10b981;
        font-weight: 700;
        margin-bottom: 6px;
        display: flex;
        align-items: center;
        gap: 4px;
    }
    .card-ai-reasoning-text {
        font-size: 0.8rem;
        color: #94a3b8;
        line-height: 1.4;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Filter tabs
    all_cats = list(dict.fromkeys([a.get("category","") for a in attractions]))
    tabs_labels = ["All"] + all_cats
    tabs = st.tabs(tabs_labels)

    for ti, tab in enumerate(tabs):
        with tab:
            filtered = attractions if ti == 0 else [a for a in attractions if a.get("category","") == all_cats[ti-1]]
            
            grid_html = "<div class='grid-container'>"
            for i, a in enumerate(filtered):
                name = a.get("name", "Attraction")
                fee = a.get("entry_fee_usd", 0)
                fee_str = "Free" if fee == 0 else f"${fee:.0f}"
                img_url = a.get("image_url") or f"https://picsum.photos/seed/{abs(hash(name))}/800/500"
                badge = f"#{i+1} Must See"
                desc = a.get("description", "")
                cat = a.get("category", "Landmark")
                
                tags_html = f"<span class='card-tag'>{cat}</span>"
                for tag in a.get("tags", [])[:2]:
                    tags_html += f"<span class='card-tag'>{tag}</span>"
                    
                grid_html += f"""
<div class='image-card'>
    <div class='card-image-container'>
        <div class='card-badge'>{badge}</div>
        <img src='{img_url}' alt='{name}'>
    </div>
    <div class='card-content'>
        <div class='card-title-row'>
            <div class='card-title' title='{name}'>{name}</div>
            <div class='card-price'>{fee_str}</div>
        </div>
        <div class='card-tags'>
            {tags_html}
        </div>
    </div>
    <div class='card-ai-reasoning'>
        <div class='card-ai-reasoning-title'>🎯 Attraction Insight:</div>
        <div class='card-ai-reasoning-text'>{desc}</div>
    </div>
</div>
"""
            grid_html += "</div>"
            st.markdown(grid_html, unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
# SECTION 3 — NEARBY SERVICES
# ════════════════════════════════════════════════════════════════════════════
sec("🏪", "Nearby Services & Essentials")

svc_type_order = ["restaurant","cafe","atm","pharmacy","hospital","taxi","supermarket","spa","mosque"]
svc_labels = {
    "restaurant":"🍽️ Restaurants","cafe":"☕ Cafes & Bakeries","atm":"🏧 ATMs & Banking",
    "pharmacy":"💊 Pharmacies","hospital":"🏥 Medical","taxi":"🚕 Transport",
    "supermarket":"🛒 Markets","spa":"💆 Wellness & Spa","mosque":"🕌 Places of Worship",
}
svc_colors = {
    "restaurant":"#e94560","cafe":"#f5a623","atm":"#10b981","pharmacy":"#06b6d4",
    "hospital":"#0ea5e9","taxi":"#fb923c","supermarket":"#7c3aed","spa":"#f472b6","mosque":"#8b5cf6",
}

if not services:
    st.info("No nearby services data — plan a trip to populate this section.")
else:
    # Group by type
    grouped = {}
    for svc in services:
        t = svc.get("service_type","other")
        grouped.setdefault(t, []).append(svc)

    ordered_types = [t for t in svc_type_order if t in grouped] + [t for t in grouped if t not in svc_type_order]
    tab_labels = [svc_labels.get(t, t.title()) for t in ordered_types]
    tabs_svc = st.tabs(tab_labels)

    for tab_i, stype in enumerate(ordered_types):
        with tabs_svc[tab_i]:
            svcs = grouped[stype]
            color = svc_colors.get(stype, "#94a3b8")
            cols = st.columns(min(3, len(svcs)))
            for j, svc in enumerate(svcs):
                sname = svc.get("name","")
                icon  = svc.get("category_icon","📍")
                rat   = svc.get("rating",0)
                dist  = svc.get("distance_m",0)
                price = svc.get("price_level","")
                desc  = svc.get("description","")
                open_ = svc.get("open_now", True)
                tags  = svc.get("tags",[])
                addr  = svc.get("address","")

                dist_label = f"{dist}m" if dist < 1000 else f"{dist/1000:.1f}km"
                open_html  = "<span style='color:#10b981;font-size:0.72rem;'>● Open</span>" if open_ else "<span style='color:#e94560;font-size:0.72rem;'>● Closed</span>"
                stars_s    = "⭐" * int(rat) if rat > 0 else ""
                tags_s     = " · ".join(tags[:3])

                with cols[j % len(cols)]:
                    st.markdown(f"""
                    <div style='background:linear-gradient(135deg,rgba(22,33,62,0.9),rgba(15,12,41,0.7));
                                border:1px solid {color}40;border-top:3px solid {color};border-radius:12px;
                                padding:16px;margin-bottom:12px;height:100%;'>
                      <div style='display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;'>
                        <div style='display:flex;align-items:center;gap:8px;'>
                          <span style='font-size:1.6rem;'>{icon}</span>
                          <div>
                            <div style='font-weight:700;color:#f8fafc;font-size:0.9rem;'>{sname}</div>
                            {open_html}
                          </div>
                        </div>
                        <div style='text-align:right;'>
                          <div style='color:#f5a623;font-size:0.78rem;'>{stars_s} {rat if rat>0 else ""}</div>
                          <div style='color:#64748b;font-size:0.7rem;'>{price}</div>
                        </div>
                      </div>
                      <p style='color:#94a3b8;font-size:0.8rem;line-height:1.4;margin:0 0 8px 0;'>{desc[:120]}</p>
                      <div style='display:flex;gap:14px;border-top:1px solid rgba(255,255,255,0.06);padding-top:8px;'>
                        <span style='font-size:0.75rem;color:#64748b;'>📍 {dist_label} away</span>
                        {f'<span style="font-size:0.75rem;color:#64748b;">{tags_s}</span>' if tags_s else ''}
                      </div>
                    </div>""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
# SECTION 4 — SERVICES DONUT CHART
# ════════════════════════════════════════════════════════════════════════════
if services:
    st.markdown("<div style='margin-top:10px;'></div>", unsafe_allow_html=True)
    chart_col, info_col = st.columns([1, 1])

    with chart_col:
        st.markdown("#### 📊 Services Distribution")
        svc_counts = Counter([s.get("service_type","other") for s in services])
        labels = [svc_labels.get(k, k.title()) for k in svc_counts.keys()]
        values = list(svc_counts.values())
        colors_pie = [svc_colors.get(k,"#94a3b8") for k in svc_counts.keys()]
        fig_pie = go.Figure(go.Pie(
            labels=labels, values=values,
            marker=dict(colors=colors_pie, line=dict(color="#1a1a2e", width=2)),
            hole=0.55, textinfo="label+percent",
            textfont=dict(color="#f8fafc", size=10),
        ))
        fig_pie.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#94a3b8"),
            legend=dict(bgcolor="rgba(22,33,62,0.5)", font=dict(color="#f8fafc")),
            margin=dict(t=10,b=10,l=10,r=10), height=300,
            annotations=[dict(text=f"<b>{len(services)}</b><br>Services", x=0.5, y=0.5,
                              font_size=14, showarrow=False, font=dict(color="#f8fafc"))]
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    with info_col:
        st.markdown("#### 🏆 Highest Rated Nearby")
        top_svcs = sorted(services, key=lambda s: s.get("rating",0), reverse=True)[:5]
        for svc in top_svcs:
            color = svc_colors.get(svc.get("service_type",""), "#94a3b8")
            rat   = svc.get("rating", 0)
            bar_w = int(rat / 5 * 100)
            st.markdown(f"""
            <div style='display:flex;align-items:center;gap:10px;margin-bottom:10px;'>
              <span style='font-size:1.2rem;'>{svc.get("category_icon","📍")}</span>
              <div style='flex:1;'>
                <div style='font-size:0.82rem;color:#f8fafc;font-weight:600;'>{svc.get("name","")}</div>
                <div style='height:6px;background:rgba(255,255,255,0.08);border-radius:3px;margin-top:3px;'>
                  <div style='width:{bar_w}%;height:100%;background:{color};border-radius:3px;'></div>
                </div>
              </div>
              <span style='color:#f5a623;font-size:0.82rem;font-weight:700;'>⭐ {rat}</span>
            </div>""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
# SECTION 5 — DAY-BY-DAY SCHEDULE + WEATHER
# ════════════════════════════════════════════════════════════════════════════
sec("📅", "Day-by-Day Schedule with Weather Impact")

start_date = result.get("start_date", "")
end_date = result.get("end_date", "")
dates_param = ""
if start_date and end_date:
    try:
        sd = start_date.replace("-", "")
        ed = end_date.replace("-", "")
        dates_param = f"&dates={sd}/{ed}"
    except:
        pass

gcal_url = f"https://www.google.com/calendar/render?action=TEMPLATE&text=Trip+to+{destination.replace(' ', '+')}&details=Full+Itinerary+Generated+by+AI+Travel&location={destination.replace(' ', '+')}{dates_param}"

st.markdown(f"""
<div style='display:flex; justify-content:flex-end; margin-top:-45px; margin-bottom:25px; position:relative; z-index:10;'>
    <a href='{gcal_url}' target='_blank' style='background:rgba(22,33,62,0.8); border:1px solid #7c3aed; color:#a78bfa; text-decoration:none; padding:8px 16px; border-radius:8px; font-size:0.85rem; font-weight:600; display:flex; align-items:center; gap:8px; transition:all 0.3s ease;'>
        <span>🗓️ Schedule on Google Calendar</span>
    </a>
</div>
""", unsafe_allow_html=True)

for day in itinerary:
    day_num  = day.get("day_number", 1)
    title    = day.get("title", "")
    activities = day.get("activities", [])
    meals    = day.get("meals", [])
    accom    = day.get("accommodation", "")
    cost     = day.get("estimated_daily_cost_usd", 0)
    notes    = day.get("notes", "")

    temp_h, temp_l, icon_w, cond, precip = 25, 18, "🌤️", "Clear", 0
    w_color, w_label = "#0ea5e9", "Pleasant"
    if forecast and day_num <= len(forecast):
        wd = forecast[day_num - 1]
        temp_h  = wd.get("temp_high_c", 25)
        temp_l  = wd.get("temp_low_c", 18)
        icon_w  = wd.get("icon", "🌤️")
        cond    = wd.get("condition", "Clear")
        precip  = wd.get("precipitation_mm", 0)
        w_color, w_label = weather_color(precip, temp_h)

    if precip > 10:   impact_msg, impact_clr = "🌧️ Heavy rain — indoor activities recommended", "#60a5fa"
    elif precip > 5:  impact_msg, impact_clr = "🌦️ Light rain possible — carry umbrella", "#93c5fd"
    elif temp_h > 35: impact_msg, impact_clr = "🔥 Very hot — outdoor visits before 11 AM", "#f87171"
    elif temp_h > 28: impact_msg, impact_clr = "☀️ Warm & sunny — perfect outdoor day, stay hydrated", "#fb923c"
    else:             impact_msg, impact_clr = "✅ Ideal weather — all outdoor attractions accessible", "#34d399"

    morning_acts = afternoon_acts = evening_acts = []
    spots_today = []
    for act in activities:
        if act.startswith("MORNING:"): morning_acts = [a.strip() for a in act.replace("MORNING:","").split("|") if a.strip()]
        elif act.startswith("AFTERNOON:"): afternoon_acts = [a.strip() for a in act.replace("AFTERNOON:","").split("|") if a.strip()]
        elif act.startswith("EVENING:"): evening_acts = [a.strip() for a in act.replace("EVENING:","").split("|") if a.strip()]

    for part in notes.split("||"):
        part = part.strip()
        if "Tourist spots" in part or "Tourist Spots" in part:
            spots_today = [s.strip() for s in part.split(":",1)[-1].split(",") if s.strip()]

    with st.expander(
        f"{'📍' if day_num==1 else '🗓️'} Day {day_num}: {title}  |  {icon_w} {temp_h:.0f}°C/{temp_l:.0f}°C  |  💰 ~${cost:.0f}",
        expanded=(day_num <= 2)
    ):
        left, right = st.columns([3, 1])
        with left:
            st.markdown(f"""
            <div style='background:rgba({",".join(str(int(x*255)) for x in mcolors.to_rgb(impact_clr))},0.08);
                        border:1px solid {impact_clr}44;border-radius:10px;
                        padding:10px 14px;margin-bottom:12px;font-size:0.88rem;color:{impact_clr};'>
                {impact_msg}</div>""", unsafe_allow_html=True)

            if spots_today:
                chips = "".join([f"<span style='background:rgba(124,58,237,0.2);color:#a78bfa;border:1px solid #7c3aed44;border-radius:20px;padding:3px 10px;font-size:0.78rem;font-weight:600;margin:2px;display:inline-block;'>📍 {s}</span>" for s in spots_today])
                st.markdown(f"<div style='margin-bottom:12px;'><div style='font-size:0.72rem;color:#94a3b8;text-transform:uppercase;letter-spacing:.08em;margin-bottom:5px;'>Today's Tourist Spots</div>{chips}</div>", unsafe_allow_html=True)

            for emoji, lbl, acts in [("🌅","Morning",morning_acts),("☀️","Afternoon",afternoon_acts),("🌙","Evening",evening_acts)]:
                if not acts: continue
                rows = "".join([f"<div style='display:flex;gap:6px;margin:3px 0;'><span style='color:#e94560;'>›</span><span style='color:#cbd5e1;font-size:0.83rem;'>{a}</span></div>" for a in acts if a])
                st.markdown(f"<div style='margin-bottom:10px;'><div style='font-weight:600;color:#f8fafc;font-size:0.85rem;margin-bottom:3px;'>{emoji} {lbl}</div>{rows}</div>", unsafe_allow_html=True)

            if meals:
                st.markdown(f"<div style='border-top:1px solid rgba(255,255,255,0.07);padding-top:8px;font-size:0.8rem;color:#64748b;'>🍽️ &nbsp;" + " &nbsp;|&nbsp; ".join([f"<span style='color:#f5a623;'>{m}</span>" for m in meals]) + "</div>", unsafe_allow_html=True)

        with right:
            st.markdown(f"""
            <div style='background:linear-gradient(135deg,{w_color}18,rgba(22,33,62,0.8));
                        border:1px solid {w_color}44;border-radius:14px;padding:16px;text-align:center;'>
              <div style='font-size:0.65rem;color:#94a3b8;text-transform:uppercase;'>Day {day_num} Weather</div>
              <div style='font-size:2.5rem;margin:6px 0;'>{icon_w}</div>
              <div style='font-weight:700;color:#f8fafc;font-size:0.88rem;'>{cond}</div>
              <div style='font-family:Space Grotesk,sans-serif;font-size:1.8rem;font-weight:800;color:{w_color};'>{temp_h:.0f}°C</div>
              <div style='font-size:0.75rem;color:#64748b;margin-bottom:8px;'>Low {temp_l:.0f}°C · Rain {precip:.0f}mm</div>
              <div style='background:{w_color}22;color:{w_color};border-radius:20px;padding:3px 10px;font-size:0.7rem;font-weight:700;'>{w_label}</div>
            </div>
            <div style='background:rgba(22,33,62,0.6);border:1px solid rgba(255,255,255,0.07);
                        border-radius:10px;padding:12px;margin-top:10px;text-align:center;'>
              <div style='font-size:0.65rem;color:#94a3b8;'>Daily Budget</div>
              <div style='font-family:Space Grotesk,sans-serif;font-size:1.4rem;font-weight:700;color:#f5a623;'>${cost:.0f}</div>
              <div style='font-size:0.68rem;color:#64748b;'>🏨 {accom[:22]}{"..." if len(accom)>22 else ""}</div>
            </div>""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
# SECTION 6 — WEATHER IMPACT CHARTS
# ════════════════════════════════════════════════════════════════════════════
if forecast and len(forecast) >= 2:
    sec("🌡️", "Weather Impact on Your Trip")

    days_l = [d.get("date", f"Day {i+1}") for i, d in enumerate(forecast)]
    highs  = [d.get("temp_high_c", 0) for d in forecast]
    lows   = [d.get("temp_low_c", 0) for d in forecast]
    rains  = [d.get("precipitation_mm", 0) for d in forecast]

    outdoor_scores = []
    for d in forecast:
        s = 80
        if d.get("precipitation_mm",0) > 10: s -= 30
        elif d.get("precipitation_mm",0) > 5: s -= 15
        if d.get("temp_high_c",0) > 35: s -= 15
        if d.get("humidity_pct",0) > 85: s -= 10
        outdoor_scores.append(max(20, min(100, s)))

    bar_clr = ["#10b981" if s>=75 else "#f5a623" if s>=55 else "#e94560" for s in outdoor_scores]

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("#### 🌡️ Temperature & Rainfall")
        fig_t = go.Figure()
        fig_t.add_trace(go.Scatter(x=days_l, y=highs, name="High °C", line=dict(color="#e94560",width=3), mode="lines+markers", marker=dict(size=9)))
        fig_t.add_trace(go.Scatter(x=days_l, y=lows, name="Low °C", line=dict(color="#0ea5e9",width=3), fill="tonexty", fillcolor="rgba(14,165,233,0.1)", mode="lines+markers", marker=dict(size=9)))
        fig_t.add_trace(go.Bar(x=days_l, y=rains, name="Rain mm", yaxis="y2", marker_color="rgba(96,165,250,0.3)", width=0.4))
        fig_t.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(22,33,62,0.3)", font=dict(color="#94a3b8"),
            xaxis=dict(gridcolor="rgba(255,255,255,0.05)"), yaxis=dict(gridcolor="rgba(255,255,255,0.05)", ticksuffix="°C"),
            yaxis2=dict(overlaying="y", side="right", showgrid=False, tickfont=dict(color="#60a5fa")),
            legend=dict(bgcolor="rgba(22,33,62,0.5)"), margin=dict(t=20,b=10,l=40,r=50), height=280)
        st.plotly_chart(fig_t, use_container_width=True)

    with c2:
        st.markdown("#### 🌿 Daily Outdoor Suitability")
        fig_s = go.Figure(go.Bar(x=days_l, y=outdoor_scores, marker=dict(color=bar_clr, line=dict(color="#1a1a2e",width=1)),
            text=[f"{s}%" for s in outdoor_scores], textposition="outside", textfont=dict(color="#f8fafc",size=10)))
        fig_s.add_hline(y=75, line=dict(color="#10b981",dash="dot",width=1.5), annotation_text="Good", annotation_font_color="#10b981")
        fig_s.add_hline(y=55, line=dict(color="#f5a623",dash="dot",width=1.5), annotation_text="Fair", annotation_font_color="#f5a623")
        fig_s.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(22,33,62,0.3)", font=dict(color="#94a3b8"),
            xaxis=dict(gridcolor="rgba(255,255,255,0.05)"), yaxis=dict(gridcolor="rgba(255,255,255,0.05)", ticksuffix="%", range=[0,110]),
            margin=dict(t=20,b=10,l=40,r=10), height=280)
        st.plotly_chart(fig_s, use_container_width=True)

    best_i  = outdoor_scores.index(max(outdoor_scores))
    worst_i = outdoor_scores.index(min(outdoor_scores))
    avg_s   = sum(outdoor_scores)/len(outdoor_scores)
    ia1, ia2, ia3 = st.columns(3)
    with ia1:
        bfc = forecast[best_i]
        st.markdown(f"<div style='background:rgba(16,185,129,0.1);border:1px solid rgba(16,185,129,0.4);border-radius:12px;padding:14px;text-align:center;'><div style='font-size:0.72rem;color:#94a3b8;'>BEST DAY FOR OUTDOORS</div><div style='font-size:1.4rem;margin:4px 0;'>{bfc.get('icon','🌤️')}</div><div style='font-weight:700;color:#10b981;'>{bfc.get('date',f'Day {best_i+1}')}</div><div style='font-size:0.78rem;color:#64748b;'>{bfc.get('condition','')} · {bfc.get('temp_high_c',0):.0f}°C</div></div>", unsafe_allow_html=True)
    with ia2:
        wfc = forecast[worst_i]
        st.markdown(f"<div style='background:rgba(233,69,96,0.1);border:1px solid rgba(233,69,96,0.4);border-radius:12px;padding:14px;text-align:center;'><div style='font-size:0.72rem;color:#94a3b8;'>MOST CHALLENGING DAY</div><div style='font-size:1.4rem;margin:4px 0;'>{wfc.get('icon','🌧️')}</div><div style='font-weight:700;color:#e94560;'>{wfc.get('date',f'Day {worst_i+1}')}</div><div style='font-size:0.78rem;color:#64748b;'>{wfc.get('condition','')} · {wfc.get('temp_high_c',0):.0f}°C</div></div>", unsafe_allow_html=True)
    with ia3:
        sc2 = "#10b981" if avg_s >= 70 else "#f5a623"
        st.markdown(f"<div style='background:rgba(124,58,237,0.1);border:1px solid rgba(124,58,237,0.4);border-radius:12px;padding:14px;text-align:center;'><div style='font-size:0.72rem;color:#94a3b8;'>OVERALL TRIP WEATHER</div><div style='font-family:Space Grotesk,sans-serif;font-size:2rem;font-weight:800;color:{sc2};margin:4px 0;'>{avg_s:.0f}%</div><div style='font-size:0.78rem;color:#64748b;'>Avg outdoor suitability</div></div>", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
# SECTION 7 — PDF DOWNLOAD
# ════════════════════════════════════════════════════════════════════════════
sec("📄", "Download Your Travel Report (PDF)")

st.markdown(f"""
<div style='background:linear-gradient(135deg,rgba(233,69,96,0.1),rgba(245,166,35,0.08));
            border:1px solid rgba(233,69,96,0.3);border-radius:16px;padding:20px;margin-bottom:20px;'>
  <div style='display:flex;align-items:center;gap:16px;flex-wrap:wrap;'>
    <span style='font-size:3rem;'>📑</span>
    <div>
      <div style='font-family:Space Grotesk,sans-serif;font-size:1.05rem;font-weight:700;color:#f8fafc;margin-bottom:4px;'>
        AI Travel Report — {destination}</div>
      <div style='font-size:0.82rem;color:#94a3b8;'>
        Includes: Tourist places · Nearby services · Day-by-day schedule ·
        Weather analysis • Hotels & Resorts • Budget • Flights • Review insights
      </div>
    </div>
  </div>
</div>""", unsafe_allow_html=True)

pdf_col1, pdf_col2 = st.columns(2)
with pdf_col1:
    if st.button("📄 Generate & Download PDF Report", use_container_width=True):
        if not trip_id:
            st.error("Trip ID not found. Please re-plan your trip.")
        else:
            with st.spinner("Generating your professional PDF report..."):
                try:
                    gen = requests.post(f"{BACKEND_URL}/api/reports/generate",
                        json={"trip_id": trip_id, "session_id": SESSION_ID}, timeout=60)
                    if gen.status_code == 200:
                        rep = gen.json()
                        rep_id   = rep.get("report_id")
                        filename = rep.get("pdf_filename", "travel_report.pdf")
                        dl = requests.get(f"{BACKEND_URL}/api/reports/download/{rep_id}", timeout=30)
                        if dl.status_code == 200:
                            st.session_state.pdf_bytes    = dl.content
                            st.session_state.pdf_filename = filename
                            st.success(f"✅ PDF ready: **{filename}** ({len(dl.content)//1024} KB)")
                        else:
                            st.error("Failed to download PDF.")
                    else:
                        st.error(f"Generation failed: {gen.text[:200]}")
                except requests.exceptions.ConnectionError:
                    st.error("Cannot reach backend. Make sure it is running on port 8000.")
                except Exception as e:
                    st.error(f"Error: {e}")

with pdf_col2:
    if st.session_state.get("pdf_bytes"):
        st.download_button(label="⬇️ Click Here to Save PDF",
            data=st.session_state["pdf_bytes"],
            file_name=st.session_state.get("pdf_filename","travel_report.pdf"),
            mime="application/pdf", use_container_width=True)
        st.markdown(f"""<div style='background:rgba(16,185,129,0.1);border:1px solid rgba(16,185,129,0.3);
            border-radius:10px;padding:10px;margin-top:8px;text-align:center;'>
            <div style='color:#10b981;font-weight:600;font-size:0.88rem;'>✅ Report Ready to Download</div>
            <div style='color:#64748b;font-size:0.72rem;'>{st.session_state.get("pdf_filename","")}</div></div>""",
            unsafe_allow_html=True)

# WhatsApp
st.markdown("---")
st.markdown("### 📲 Send Report via WhatsApp")
wa1, wa2 = st.columns([2,1])
with wa1:
    wa_num = st.text_input("WhatsApp Number (with country code)", placeholder="+14155552368", key="wa_out")
with wa2:
    st.markdown("<div style='padding-top:28px;'></div>", unsafe_allow_html=True)
    if st.button("📲 Send WhatsApp", use_container_width=True):
        if not wa_num:
            st.warning("Enter a phone number first.")
        else:
            with st.spinner("Sending..."):
                try:
                    r = requests.post(f"{BACKEND_URL}/api/reports/send-whatsapp",
                        json={"trip_id": trip_id, "session_id": SESSION_ID, "phone_number": wa_num}, timeout=20)
                    if r.status_code == 200:
                        st.success(f"✅ Sent to {wa_num}!")
                        note = r.json().get("data",{}).get("note","")
                        if note: st.info(note)
                    else:
                        st.error(f"Failed: {r.text[:100]}")
                except Exception as e:
                    st.error(f"Error: {e}")
