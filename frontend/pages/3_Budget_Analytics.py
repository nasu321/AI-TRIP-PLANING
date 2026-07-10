"""
Page 3: Budget Analytics
Interactive charts, budget breakdown, and currency converter.
"""
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from pathlib import Path

st.set_page_config(page_title="Budget Analytics | AI Travel", page_icon="📊", layout="wide")

css_path = Path(__file__).parent.parent / "assets" / "style.css"
if css_path.exists():
    with open(css_path, encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

st.markdown("""<style>
.stApp { background: linear-gradient(135deg, #0f0c29 0%, #1a1a2e 40%, #16213e 100%); color: #f8fafc; }
section[data-testid="stSidebar"] { background: linear-gradient(180deg, #0f0c29, #1a1a2e); }
h1,h2,h3 { color: #f8fafc; font-family: 'Space Grotesk', sans-serif; }
p, label { color: #cbd5e1; }
.stSelectbox > div > div { background: rgba(22,33,62,0.8) !important;
    border: 1px solid rgba(255,255,255,0.15) !important; color: #f8fafc !important; border-radius: 10px !important; }
.stNumberInput > div > div > input { background: rgba(22,33,62,0.8) !important;
    border: 1px solid rgba(255,255,255,0.15) !important; color: #f8fafc !important; border-radius: 10px !important; }
div[data-testid="stMetricValue"] { color: #f5a623 !important; font-size: 1.6rem !important; }
</style>""", unsafe_allow_html=True)


# Plotly dark theme helper
def dark_fig(fig):
    fig.update_layout(
        paper_bgcolor="rgba(15,12,41,0.0)",
        plot_bgcolor="rgba(22,33,62,0.4)",
        font=dict(color="#94a3b8", family="Inter"),
        title_font=dict(color="#f8fafc", size=16, family="Space Grotesk"),
        legend=dict(bgcolor="rgba(22,33,62,0.5)", bordercolor="rgba(255,255,255,0.1)"),
    )
    return fig


st.markdown("""
<div class='destination-hero'>
    <h1>📊 Budget Analytics</h1>
    <p>Detailed cost breakdown, budget fit analysis, and currency conversion</p>
</div>
""", unsafe_allow_html=True)

result = st.session_state.get("trip_result")
if not result:
    st.warning("⚠️ No trip planned yet. Go to **🗺️ Plan Trip** first.")
    st.stop()

budget = result.get("budget", {})
destination = result.get("destination", "")

# ─── Key Budget Metrics ───────────────────────────────────────
m1, m2, m3, m4 = st.columns(4)
total = budget.get("total_estimated_usd", 0)
user_budget = result.get("travel_score", {}).get("budget_score", 70) / 100 * total * 1.2  # estimate
remaining = budget.get("budget_remaining_usd", 0)
fit_score = budget.get("budget_fit_score", 0)

with m1:
    st.metric("💰 Total Estimated", f"${total:,.0f}")
with m2:
    st.metric("💚 Remaining", f"${remaining:,.0f}", delta=f"{'Under' if remaining >= 0 else 'Over'} budget")
with m3:
    st.metric("📈 Budget Fit Score", f"{fit_score:.0f}/100")
with m4:
    st.metric("🏷️ Fit Label", budget.get("budget_fit_label", "N/A")[:15] + "...")

st.markdown(f"**Budget Assessment:** {budget.get('budget_fit_label', '')}")
st.markdown("---")

# ─── Charts Row ───────────────────────────────────────────────
chart_col1, chart_col2 = st.columns(2)

categories = {
    "✈️ Flights": budget.get("flight_cost_usd", 0),
    "🏨 Hotels": budget.get("hotel_total_usd", 0),
    "🎭 Activities": budget.get("activities_total_usd", 0),
    "🍽️ Food": budget.get("food_total_usd", 0),
    "🚌 Transport": budget.get("transport_local_usd", 0),
    "📦 Misc": budget.get("misc_usd", 0),
}

with chart_col1:
    st.markdown("#### 🍕 Budget Distribution")
    fig_pie = go.Figure(data=[go.Pie(
        labels=list(categories.keys()),
        values=list(categories.values()),
        hole=0.55,
        marker=dict(
            colors=["#e94560", "#0ea5e9", "#7c3aed", "#f5a623", "#10b981", "#64748b"],
            line=dict(color="#1a1a2e", width=2),
        ),
        textfont=dict(color="#f8fafc", size=11),
    )])
    fig_pie.update_layout(
        showlegend=True,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#94a3b8"),
        legend=dict(bgcolor="rgba(22,33,62,0.5)"),
        annotations=[dict(text=f"<b>${total:,.0f}</b>", x=0.5, y=0.5, font_size=16,
                          font_color="#f5a623", showarrow=False)],
        margin=dict(t=20, b=20, l=20, r=20),
        height=340,
    )
    st.plotly_chart(fig_pie, use_container_width=True)

with chart_col2:
    st.markdown("#### 📊 Cost Breakdown")
    fig_bar = go.Figure(data=[go.Bar(
        x=list(categories.keys()),
        y=list(categories.values()),
        marker=dict(
            color=["#e94560", "#0ea5e9", "#7c3aed", "#f5a623", "#10b981", "#64748b"],
            line=dict(color="#1a1a2e", width=1),
        ),
        text=[f"${v:,.0f}" for v in categories.values()],
        textposition="outside",
        textfont=dict(color="#f8fafc", size=10),
    )])
    fig_bar.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(22,33,62,0.3)",
        font=dict(color="#94a3b8"),
        xaxis=dict(tickfont=dict(color="#94a3b8", size=10), gridcolor="rgba(255,255,255,0.05)"),
        yaxis=dict(tickfont=dict(color="#94a3b8"), gridcolor="rgba(255,255,255,0.05)",
                   tickprefix="$"),
        margin=dict(t=40, b=20, l=40, r=20),
        height=340,
    )
    st.plotly_chart(fig_bar, use_container_width=True)

# ─── Detailed Breakdown Table ─────────────────────────────────
st.markdown("#### 💳 Itemized Budget Breakdown")
for cat, amount in categories.items():
    pct = (amount / total * 100) if total else 0
    bar_color_map = {
        "✈️ Flights": "#e94560", "🏨 Hotels": "#0ea5e9", "🎭 Activities": "#7c3aed",
        "🍽️ Food": "#f5a623", "🚌 Transport": "#10b981", "📦 Misc": "#64748b",
    }
    bar_color = bar_color_map.get(cat, "#94a3b8")
    st.markdown(f"""
    <div class='budget-item'>
        <div class='budget-category'>{cat}</div>
        <div style='flex:2; margin:0 12px;'>
            <div style='background:rgba(255,255,255,0.08); border-radius:4px; height:8px; overflow:hidden;'>
                <div style='width:{pct:.1f}%; height:100%; background:{bar_color}; border-radius:4px;'></div>
            </div>
        </div>
        <div style='color:#94a3b8; font-size:0.82rem; min-width:40px; text-align:center;'>{pct:.0f}%</div>
        <div class='budget-amount'>${amount:,.0f}</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown(f"""
<div style='background:linear-gradient(135deg,rgba(233,69,96,0.15),rgba(245,166,35,0.1));
            border:1px solid rgba(233,69,96,0.4); border-radius:12px; padding:16px;
            margin-top:12px; display:flex; justify-content:space-between;'>
    <div style='font-weight:700; font-size:1.1rem; color:#f8fafc;'>💳 TOTAL ESTIMATED COST</div>
    <div style='font-family:Space Grotesk,sans-serif; font-size:1.5rem; font-weight:800; color:#f5a623;'>
        ${total:,.0f}</div>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# ─── Cost Saving Tips ─────────────────────────────────────────
tips = budget.get("cost_saving_tips", [])
if tips:
    st.markdown("#### 💡 AI Cost-Saving Tips")
    for tip in tips:
        st.markdown(f"""
        <div class='tip-card'>💡 {tip}</div>
        """, unsafe_allow_html=True)

st.markdown("---")

# ─── Currency Converter ───────────────────────────────────────
st.markdown("#### 💱 Currency Converter")
RATES = {
    "USD": 1.0, "EUR": 1.09, "GBP": 1.27, "JPY": 0.0067, "AUD": 0.65,
    "CAD": 0.74, "CHF": 1.13, "SGD": 0.74, "AED": 0.27, "THB": 0.028,
    "IDR": 0.000063, "INR": 0.012, "MXN": 0.057, "BRL": 0.19,
}
cc1, cc2, cc3 = st.columns(3)
with cc1:
    amount_to_convert = st.number_input("Amount", value=float(total), min_value=1.0)
with cc2:
    from_curr = st.selectbox("From", list(RATES.keys()), index=0)
with cc3:
    to_curr = st.selectbox("To", list(RATES.keys()), index=list(RATES.keys()).index("EUR"))

converted = amount_to_convert * RATES[from_curr] / RATES[to_curr]
st.markdown(f"""
<div style='text-align:center; background:rgba(22,33,62,0.7); border:1px solid rgba(255,255,255,0.1);
            border-radius:12px; padding:20px; margin-top:8px;'>
    <div style='font-size:1.0rem; color:#94a3b8;'>{amount_to_convert:,.2f} {from_curr} =</div>
    <div style='font-family:Space Grotesk,sans-serif; font-size:2.5rem; font-weight:800; color:#f5a623;'>
        {converted:,.2f} {to_curr}</div>
    <div style='font-size:0.75rem; color:#64748b;'>Rate: 1 {from_curr} = {RATES[from_curr]/RATES[to_curr]:.4f} {to_curr}</div>
</div>
""", unsafe_allow_html=True)
