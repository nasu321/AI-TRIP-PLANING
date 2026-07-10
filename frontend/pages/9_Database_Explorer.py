"""
Page 9: Database Explorer — Browse linked real datasets
OpenFlights, Hotel Prices, Cost of Living, Flight Price Index
"""
import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

st.set_page_config(page_title="Database Explorer | AI Travel", page_icon="🗄️", layout="wide")

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
p,label,span,div{color:#cbd5e1;}
.stButton>button{background:linear-gradient(135deg,#7c3aed,#0ea5e9);color:white;
  border:none;border-radius:10px;font-weight:600;padding:10px 24px;width:100%;}
.stButton>button:hover{transform:translateY(-2px);box-shadow:0 8px 25px rgba(124,58,237,0.4);}
.stTextInput>div>div>input{background:rgba(22,33,62,0.9) !important;color:#f8fafc !important;
  border:1px solid rgba(255,255,255,0.1) !important;border-radius:10px !important;}
.stDataFrame{border-radius:12px;overflow:hidden;}
</style>""", unsafe_allow_html=True)

BACKEND_URL = st.session_state.get("backend_url", "http://127.0.0.1:8505")


def sec(icon, title, sub=""):
    st.markdown(f"""
    <div style='display:flex;align-items:center;gap:12px;padding-bottom:12px;
                border-bottom:2px solid #7c3aed;margin:28px 0 20px 0;'>
        <span style='font-size:1.8rem;'>{icon}</span>
        <div>
          <h2 style='margin:0;font-size:1.4rem;'>{title}</h2>
          {f'<p style="margin:0;font-size:0.82rem;color:#94a3b8;">{sub}</p>' if sub else ''}
        </div>
    </div>""", unsafe_allow_html=True)


# ── Header ───────────────────────────────────────────────────────────────────
st.markdown("""
<div style='text-align:center;padding:30px 0 10px;'>
  <h1 style='font-size:2.4rem;background:linear-gradient(135deg,#7c3aed,#0ea5e9);
             -webkit-background-clip:text;-webkit-text-fill-color:transparent;'>
    🗄️ Linked Database Explorer</h1>
  <p style='color:#94a3b8;font-size:1rem;'>
    Real open datasets powering the AI Travel Platform</p>
</div>""", unsafe_allow_html=True)

# ── Auto-Start Backend (Cloud Failsafe) ───────────────────────────────────────
import socket
import subprocess
import sys
import os
import time

def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('127.0.0.1', port)) == 0

if not is_port_in_use(8505):
    backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'backend'))
    if backend_path not in sys.path:
        sys.path.append(backend_path)
    
    log_file = os.path.join(backend_path, "backend_cloud.log")
    with open(log_file, "w") as log_f:
        subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8505"],
            cwd=backend_path,
            stdout=log_f,
            stderr=subprocess.STDOUT
        )
    time.sleep(5)
    if not is_port_in_use(8505):
        try:
            with open(log_file, "r") as f:
                err = f.read()
            st.error(f"Backend failed to start! Log:\n```text\n{err}\n```")
        except:
            st.error("Backend failed to start and logs are unreadable.")

# ── Fetch DB info ─────────────────────────────────────────────────────────────
@st.cache_data(ttl=300)
def fetch_db_info():
    try:
        r = requests.get(f"{BACKEND_URL}/api/data/info", timeout=10)
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return None

db_info = fetch_db_info()

if not db_info:
    st.error("⚠️ Cannot reach backend. Make sure it's running on http://127.0.0.1:8505")
    st.stop()

stats    = db_info.get("stats", {})
registry = db_info.get("registry", [])
sources  = db_info.get("sources", [])

# ── Dataset Stats Bar ─────────────────────────────────────────────────────────
c1,c2,c3,c4,c5,c6,c7 = st.columns(7)
def stat_card(col, icon, label, value, color):
    col.markdown(f"""
    <div style='text-align:center;background:rgba(22,33,62,0.8);border:1px solid {color}44;
                border-top:3px solid {color};border-radius:14px;padding:14px 4px;'>
        <div style='font-size:1.5rem;'>{icon}</div>
        <div style='font-family:Space Grotesk;font-size:1.6rem;font-weight:800;color:{color};'>{value:,}</div>
        <div style='font-size:0.68rem;color:#94a3b8;text-transform:uppercase;letter-spacing:.06em;'>{label}</div>
    </div>""", unsafe_allow_html=True)

stat_card(c1, "✈️", "Airports",       stats.get("airports",0),       "#0ea5e9")
stat_card(c2, "🗺️",  "Flight Routes",  stats.get("routes",0),         "#7c3aed")
stat_card(c3, "🏢", "Airlines",       stats.get("airlines",0),       "#f5a623")
stat_card(c4, "🏨", "Hotel Cities",   stats.get("hotel_cities",0),   "#10b981")
stat_card(c5, "💰", "Budget Cities",  stats.get("budget_cities",0),  "#e94560")
stat_card(c6, "🎫", "Price Routes",   stats.get("flight_routes",0),  "#06b6d4")
stat_card(c7, "🏛️", "Places",         stats.get("places",0),         "#ec4899")

# ── Source Credits ────────────────────────────────────────────────────────────
st.markdown("<div style='margin-top:20px;'></div>", unsafe_allow_html=True)
src_html = ""
for s in sources:
    src_html += f"""<a href="{s['url']}" target="_blank"
      style='background:rgba(124,58,237,0.12);border:1px solid rgba(124,58,237,0.3);
             border-radius:20px;padding:5px 14px;font-size:0.78rem;color:#a78bfa;
             text-decoration:none;margin:4px;display:inline-block;'>
      🔗 {s['name']} <span style="color:#64748b;">({s['license']})</span>
    </a>"""
st.markdown(f"<div style='text-align:center;margin-bottom:10px;'>{src_html}</div>", unsafe_allow_html=True)

# ── Live Destination Lookup ───────────────────────────────────────────────────
sec("🔍", "Live Database Lookup", "Search real data for any destination")

lu_col1, lu_col2 = st.columns([3,1])
with lu_col1:
    lookup_dest = st.text_input("Enter destination city", value="Tokyo, Japan",
                                 placeholder="e.g. Paris, France")
with lu_col2:
    st.markdown("<div style='padding-top:28px;'></div>", unsafe_allow_html=True)
    do_lookup = st.button("🔍 Search Databases", use_container_width=True)

if do_lookup and lookup_dest:
    with st.spinner(f"Querying all databases for {lookup_dest}..."):
        try:
            r = requests.get(f"{BACKEND_URL}/api/data/lookup",
                             params={"destination": lookup_dest}, timeout=15)
            if r.status_code == 200:
                lu = r.json()
            else:
                lu = None
        except Exception:
            lu = None

    if lu:
        tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(
            ["✈️ Airports & Routes","🏨 Hotel Prices","💰 Cost of Living","🎫 Flights","🛫 Airlines", "🏛️ Attractions"])

        with tab1:
            airports = lu.get("airports", [])
            if airports:
                st.markdown(f"**{len(airports)} airport(s) found from OpenFlights database:**")
                for ap in airports:
                    st.markdown(f"""
                    <div style='background:rgba(14,165,233,0.08);border:1px solid rgba(14,165,233,0.3);
                                border-left:3px solid #0ea5e9;border-radius:10px;padding:12px;margin:6px 0;'>
                        <b style='color:#f8fafc;'>✈️ {ap.get("name","")} ({ap.get("iata","")})</b><br>
                        <span style='font-size:0.83rem;color:#94a3b8;'>
                            {ap.get("city","")}, {ap.get("country","")} |
                            Coordinates: {ap.get("lat","")}, {ap.get("lon","")}
                        </span>
                    </div>""", unsafe_allow_html=True)
            else:
                st.info("No airports found in OpenFlights database for this destination.")

            routes = lu.get("real_routes", [])
            if routes:
                st.markdown(f"**{len(routes)} real routes to this destination (OpenFlights):**")
                df_routes = pd.DataFrame(routes)
                st.dataframe(df_routes, use_container_width=True,
                             column_config={"airline": "Airline Code", "src": "From", "dst": "To",
                                            "stops": "Stops", "codeshare": "Codeshare"})

        with tab2:
            hp = lu.get("hotel_prices", {})
            if hp.get("data_from_db"):
                st.success(f"✅ **Real data** from {hp['source']}")
            else:
                st.warning("⚠️ Estimated — city not in database")

            col_a, col_b, col_c = st.columns(3)
            for col, tier, price, color, icon in [
                (col_a, "Budget Hotel",  hp.get("budget_usd",0),  "#10b981","🏩"),
                (col_b, "Mid-Range",     hp.get("mid_usd",0),     "#0ea5e9","🏨"),
                (col_c, "Luxury/5-Star", hp.get("luxury_usd",0),  "#f5a623","🏰"),
            ]:
                col.markdown(f"""
                <div style='background:rgba(22,33,62,0.8);border:1px solid {color}44;
                            border-top:3px solid {color};border-radius:14px;padding:20px;text-align:center;'>
                    <div style='font-size:2rem;'>{icon}</div>
                    <div style='font-size:0.72rem;color:#94a3b8;text-transform:uppercase;'>{tier}</div>
                    <div style='font-family:Space Grotesk;font-size:2.4rem;font-weight:800;color:{color};'>
                        ${price:.0f}</div>
                    <div style='font-size:0.7rem;color:#64748b;'>per night / USD</div>
                </div>""", unsafe_allow_html=True)

            st.markdown(f"""
            <div style='margin-top:14px;background:rgba(22,33,62,0.6);border-radius:10px;padding:12px;'>
                <span style='color:#94a3b8;font-size:0.82rem;'>
                    📍 City: <b style='color:#f8fafc;'>{hp.get("city","")}, {hp.get("country","")}</b> |
                    ⭐ Avg Rating: <b style='color:#f5a623;'>{hp.get("avg_rating","")} / 5</b> |
                    📈 Demand Index: <b style='color:#0ea5e9;'>{hp.get("demand_index","")}/100</b>
                </span>
            </div>""", unsafe_allow_html=True)

        with tab3:
            col_data = lu.get("cost_of_living", {})
            if col_data.get("data_from_db"):
                st.success(f"✅ **Numbeo data** from {col_data['source']}")
            else:
                st.warning("⚠️ Estimated — city not in Numbeo database")

            idx = col_data.get("numbeo_index", 60)
            st.markdown(f"""
            <div style='background:rgba(124,58,237,0.1);border:1px solid rgba(124,58,237,0.3);
                        border-radius:14px;padding:16px;margin-bottom:16px;'>
                <div style='display:flex;align-items:center;gap:20px;'>
                    <div style='text-align:center;min-width:80px;'>
                        <div style='font-family:Space Grotesk;font-size:2.5rem;font-weight:800;color:#7c3aed;'>{idx}</div>
                        <div style='font-size:0.7rem;color:#94a3b8;'>Numbeo Index<br>(NYC=100)</div>
                    </div>
                    <div style='flex:1;'>
                        <div style='height:10px;background:rgba(255,255,255,0.08);border-radius:5px;'>
                            <div style='width:{min(idx,100)}%;height:100%;background:linear-gradient(90deg,#10b981,#7c3aed);border-radius:5px;'></div>
                        </div>
                        <div style='margin-top:8px;font-size:0.82rem;color:#94a3b8;'>
                            {"🟢 Budget-friendly" if idx < 50 else "🟡 Moderate cost" if idx < 80 else "🔴 Expensive city"}
                        </div>
                    </div>
                </div>
            </div>""", unsafe_allow_html=True)

            met1, met2, met3 = st.columns(3)
            for m, label, bpk, mid, lux, unit in [
                (met1, "Daily Budget", col_data.get("daily_backpacker",0), col_data.get("daily_mid",0), col_data.get("daily_luxury",0), "/day"),
                (met2, "Meals", col_data.get("meal_cheap",0), col_data.get("meal_mid",0), col_data.get("meal_fine",0), "/meal"),
            ]:
                m.markdown(f"""
                <div style='background:rgba(22,33,62,0.6);border-radius:12px;padding:14px;'>
                    <div style='font-weight:600;color:#f8fafc;margin-bottom:8px;'>{label}</div>
                    <div style='font-size:0.82rem;color:#10b981;'>🎒 Budget: <b>${bpk:.0f}{unit}</b></div>
                    <div style='font-size:0.82rem;color:#0ea5e9;'>🧳 Mid: <b>${mid:.0f}{unit}</b></div>
                    <div style='font-size:0.82rem;color:#f5a623;'>💎 Luxury: <b>${lux:.0f}{unit}</b></div>
                </div>""", unsafe_allow_html=True)
            met3.markdown(f"""
            <div style='background:rgba(22,33,62,0.6);border-radius:12px;padding:14px;'>
                <div style='font-weight:600;color:#f8fafc;margin-bottom:8px;'>Daily Extras</div>
                <div style='font-size:0.82rem;color:#0ea5e9;'>🚌 Transport: <b>${col_data.get("local_transport_day",0):.0f}/day</b></div>
                <div style='font-size:0.82rem;color:#7c3aed;'>🎫 Attractions: <b>${col_data.get("attraction_avg",0):.0f}/visit</b></div>
            </div>""", unsafe_allow_html=True)

        with tab4:
            fp = lu.get("flight_prices", {})
            if fp.get("data_from_db"):
                st.success(f"✅ **IATA data** from {fp['source']}")
            else:
                st.warning("⚠️ Estimated — route not in IATA database")

            fa, fb, fc = st.columns(3)
            for col, lbl, val, color in [
                (fa, "Avg Round-Trip", f"${fp.get('avg_roundtrip_usd',0):,.0f}", "#0ea5e9"),
                (fb, "Min Price (Seen)", f"${fp.get('min_price_usd',0):,.0f}", "#10b981"),
                (fc, "Avg Duration", f"{fp.get('avg_duration_hours',0):.1f}h", "#f5a623"),
            ]:
                col.markdown(f"""
                <div style='background:rgba(22,33,62,0.8);border:1px solid {color}44;border-top:3px solid {color};
                            border-radius:14px;padding:20px;text-align:center;'>
                    <div style='font-size:0.72rem;color:#94a3b8;text-transform:uppercase;'>{lbl}</div>
                    <div style='font-family:Space Grotesk;font-size:2.2rem;font-weight:800;color:{color};'>{val}</div>
                    <div style='font-size:0.7rem;color:#64748b;'>From {fp.get("origin_region","")}</div>
                </div>""", unsafe_allow_html=True)

            airlines_fp = fp.get("airlines", [])
            if airlines_fp:
                chips = "".join([f"<span style='background:rgba(14,165,233,0.15);color:#38bdf8;border:1px solid rgba(14,165,233,0.3);border-radius:20px;padding:4px 12px;font-size:0.8rem;margin:3px;display:inline-block;'>✈️ {a.strip()}</span>" for a in airlines_fp])
                st.markdown(f"<div style='margin-top:14px;'><b style='color:#f8fafc;font-size:0.85rem;'>Airlines on this route (IATA):</b><br>{chips}</div>", unsafe_allow_html=True)

        with tab5:
            airlines = lu.get("airlines", [])
            if airlines:
                st.markdown(f"**{len(airlines)} real airlines from OpenFlights routes database:**")
                chips2 = "".join([f"<span style='background:rgba(124,58,237,0.15);color:#a78bfa;border:1px solid rgba(124,58,237,0.3);border-radius:20px;padding:4px 14px;font-size:0.83rem;margin:4px;display:inline-block;'>✈️ {a}</span>" for a in airlines])
                st.markdown(f"<div style='margin-top:8px;line-height:2.5;'>{chips2}</div>", unsafe_allow_html=True)
            else:
                st.info("No airlines found in OpenFlights routes for this destination.")
                
        with tab6:
            attrs = lu.get("attractions", [])
            if attrs:
                st.success(f"✅ Found **{len(attrs)} attractions** in the International Tourist Places DB.")
                df_attrs = pd.DataFrame(attrs)
                st.dataframe(df_attrs[["place_name", "category", "rating", "entry_fee_usd", "best_time_to_visit", "description"]], use_container_width=True)
            else:
                st.info("No tourist attractions found in the database for this destination.")
    else:
        st.error("Lookup failed — check backend connection.")

# ── Dataset Registry ─────────────────────────────────────────────────────────
sec("📋", "Dataset Registry", "All linked open data sources")

if registry:
    for ds in registry:
        color = {"OpenFlights Airports":"#0ea5e9","OpenFlights Routes":"#7c3aed",
                 "OpenFlights Airlines":"#f5a623","Country Codes":"#10b981",
                 "International Hotel Prices":"#e94560","Global Cost of Living":"#06b6d4",
                 "International Flight Price Index":"#fb923c","International Tourist Places":"#ec4899"}.get(ds["name"],"#94a3b8")
        st.markdown(f"""
        <div style='background:rgba(22,33,62,0.7);border:1px solid {color}33;
                    border-left:4px solid {color};border-radius:12px;
                    padding:16px;margin-bottom:10px;'>
            <div style='display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:8px;'>
                <div>
                    <b style='color:#f8fafc;font-size:1rem;'>{ds["name"]}</b>
                    <span style='background:{color}22;color:{color};border-radius:12px;padding:2px 8px;
                                 font-size:0.72rem;font-weight:600;margin-left:8px;'>{ds["license"]}</span>
                    <br><span style='font-size:0.8rem;color:#94a3b8;'>📁 {ds["file"]} &nbsp;|&nbsp;
                        📊 {ds["records"]}</span>
                    <br><span style='font-size:0.75rem;color:#64748b;'>🔗 {ds["source"]}</span>
                    <br><span style='font-size:0.75rem;color:#64748b;'>Fields: {ds["fields"]}</span>
                </div>
            </div>
        </div>""", unsafe_allow_html=True)

# ── Full Tables ───────────────────────────────────────────────────────────────
sec("📊", "Browse Full Databases")

data_path = Path(__file__).parent.parent.parent / "backend" / "app" / "data"

tab_p, tab_h, tab_b, tab_f = st.tabs(["🏛️ Tourist Places (50+ countries)", "🏨 Hotel Prices (64 cities)", "💰 Cost of Living (54 cities)", "🎫 Flight Price Index (51 routes)"])

def load_csv(filename):
    try:
        return pd.read_csv(data_path / filename, encoding="utf-8")
    except Exception:
        return pd.DataFrame()

with tab_p:
    df_p = load_csv("international_places.csv")
    if not df_p.empty:
        fig_p = px.pie(df_p, names="country", title="Tourist Attractions by Country", hole=0.3,
                       color_discrete_sequence=px.colors.qualitative.Pastel)
        fig_p.update_layout(paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(22,33,62,0.3)",
                            font=dict(color="#94a3b8"),height=380)
        st.plotly_chart(fig_p, use_container_width=True)
        st.dataframe(df_p.drop(columns=["source"],errors="ignore"), use_container_width=True)

with tab_h:
    df_h = load_csv("international_hotel_prices.csv")
    if not df_h.empty:
        # Visualisation
        fig_h = px.scatter(df_h, x="mid_hotel_usd", y="avg_rating",
                           size="demand_index", color="country",
                           hover_name="city", text="city",
                           title="Hotel Mid-Range Price vs Rating by City",
                           labels={"mid_hotel_usd":"Mid-Range Price (USD/night)","avg_rating":"Avg Rating"})
        fig_h.update_layout(paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(22,33,62,0.3)",
                            font=dict(color="#94a3b8"),height=380)
        st.plotly_chart(fig_h, use_container_width=True)
        st.dataframe(df_h.drop(columns=["source"],errors="ignore"), use_container_width=True,
                     column_config={"budget_hotel_usd":"Budget ($)","mid_hotel_usd":"Mid ($)",
                                    "luxury_hotel_usd":"Luxury ($)","avg_rating":"Rating",
                                    "demand_index":"Demand"})

with tab_b:
    df_b = load_csv("cost_of_living.csv")
    if not df_b.empty:
        df_b_sorted = df_b.sort_values("numbeo_index", ascending=False).head(30)
        fig_b = px.bar(df_b_sorted, x="city", y="numbeo_index", color="numbeo_index",
                       color_continuous_scale=["#10b981","#f5a623","#e94560"],
                       title="Numbeo Cost of Living Index (Top 30 Cities) — NYC=100",
                       labels={"numbeo_index":"Cost Index","city":"City"})
        fig_b.update_layout(paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(22,33,62,0.3)",
                            font=dict(color="#94a3b8"),height=360,xaxis_tickangle=-45)
        st.plotly_chart(fig_b, use_container_width=True)
        st.dataframe(df_b.drop(columns=["source"],errors="ignore"), use_container_width=True,
                     column_config={"daily_backpacker":"Budget/day","daily_mid":"Mid/day",
                                    "daily_luxury":"Luxury/day","numbeo_index":"Numbeo Index"})

with tab_f:
    df_f = load_csv("flight_price_index.csv")
    if not df_f.empty:
        fig_f = px.bar(df_f.sort_values("avg_roundtrip_usd"),
                       x="destination_city", y="avg_roundtrip_usd",
                       color="origin_region", barmode="group",
                       title="Average Round-Trip Flight Prices by Destination & Origin Region",
                       labels={"avg_roundtrip_usd":"Avg Price (USD)","destination_city":"Destination"})
        fig_f.update_layout(paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(22,33,62,0.3)",
                            font=dict(color="#94a3b8"),height=380,xaxis_tickangle=-45)
        st.plotly_chart(fig_f, use_container_width=True)
        st.dataframe(df_f.drop(columns=["source"],errors="ignore"), use_container_width=True,
                     column_config={"avg_roundtrip_usd":"Avg Price","min_price_usd":"Min Price",
                                    "avg_duration_hours":"Duration (h)"})
