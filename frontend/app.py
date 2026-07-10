"""
Agentic AI Smart Travel Platform — Streamlit Main Application
Premium dark-mode dashboard with multi-page navigation.
"""
import streamlit as st
import os
import sys
import time
import socket
import subprocess
from pathlib import Path

def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('127.0.0.1', port)) == 0

# Start backend if not running
if not is_port_in_use(8505):
    backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend'))
    sys.path.append(backend_path)
    # Start the FastAPI server in the background
    subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8505"],
        cwd=backend_path
    )
    # Give it a moment to boot up
    time.sleep(3)

# ─── Page Config (must be first Streamlit call) ──────────────
st.set_page_config(
    page_title="AI Travel Platform",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "Get Help": "mailto:support@aitravel.com",
        "About": "# Agentic AI Travel Platform\nPowered by LangGraph Multi-Agent AI",
    },
)

# ─── Load Custom CSS ─────────────────────────────────────────
def load_css():
    css_path = Path(__file__).parent / "assets" / "style.css"
    if css_path.exists():
        with open(css_path, encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

# ─── Apply Global Dark Theme ─────────────────────────────────
st.markdown("""
<style>
/* Override Streamlit defaults with premium dark theme */
.stApp {
    background: linear-gradient(135deg, #0f0c29 0%, #1a1a2e 40%, #16213e 100%);
    color: #f8fafc;
}
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f0c29 0%, #1a1a2e 100%);
    border-right: 1px solid rgba(255,255,255,0.08);
}
.stButton > button {
    background: linear-gradient(135deg, #e94560, #f5a623);
    color: white;
    border: none;
    border-radius: 10px;
    font-weight: 600;
    padding: 10px 24px;
    font-size: 0.95rem;
    transition: all 0.2s ease;
    width: 100%;
}
.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(233, 69, 96, 0.4);
}
.stTextInput > div > div > input,
.stSelectbox > div > div,
.stDateInput > div > div > input,
.stNumberInput > div > div > input {
    background: rgba(22, 33, 62, 0.8) !important;
    border: 1px solid rgba(255,255,255,0.15) !important;
    color: #f8fafc !important;
    border-radius: 10px !important;
}
.stSelectbox > div > div { border-radius: 10px !important; }
.stSlider > div { color: #f8fafc; }
div[data-testid="stMetricValue"] {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.8rem !important;
    font-weight: 700;
    color: #f5a623;
}
div[data-testid="stMetricLabel"] { color: #94a3b8; font-size: 0.8rem; }
.stExpander { background: rgba(22, 33, 62, 0.6); border-radius: 12px; border: 1px solid rgba(255,255,255,0.08); }
.stTabs [data-baseweb="tab-list"] { background: rgba(22, 33, 62, 0.5); border-radius: 10px; }
.stTabs [data-baseweb="tab"] { color: #94a3b8; }
.stTabs [aria-selected="true"] { color: #f5a623; background: rgba(233, 69, 96, 0.15); }
h1, h2, h3 { color: #f8fafc; font-family: 'Space Grotesk', sans-serif; }
p, span, label { color: #cbd5e1; }
.stMarkdown a { color: #e94560; }
div[data-testid="stSidebarContent"] .stMarkdown { color: #94a3b8; }
.stProgress > div > div { background: linear-gradient(90deg, #e94560, #f5a623); }
</style>
""", unsafe_allow_html=True)

# ─── Session State Init ───────────────────────────────────────
import uuid
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())[:8]

if "trip_result" not in st.session_state:
    st.session_state.trip_result = None

if "backend_url" not in st.session_state:
    st.session_state.backend_url = os.getenv("BACKEND_URL", "http://127.0.0.1:8505")

# ─── Sidebar ──────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='text-align:center; padding: 20px 0 10px 0;'>
        <div style='font-size:2.5rem; margin-bottom:8px;'>🌍</div>
        <div style='font-family: Space Grotesk, sans-serif; font-size:1.2rem;
                    font-weight:700; color:#f8fafc; margin-bottom:4px;'>AI Travel Platform</div>
        <div style='font-size:0.75rem; color:#94a3b8;'>Powered by LangGraph Agents</div>
    </div>
    <hr style='border:none; border-top: 1px solid rgba(255,255,255,0.1); margin: 8px 0 16px 0;'>
    """, unsafe_allow_html=True)

    # Session badge
    st.markdown(f"""
    <div style='background: rgba(233,69,96,0.1); border:1px solid rgba(233,69,96,0.3);
                border-radius:8px; padding:8px 12px; margin-bottom:16px; font-size:0.8rem; color:#94a3b8;'>
        🔑 Session: <code style='color:#f5a623;'>{st.session_state.session_id}</code>
    </div>
    """, unsafe_allow_html=True)

    # Navigation info
    st.markdown("""
    <div style='color:#94a3b8; font-size:0.8rem; margin-bottom:12px;'>
        📌 <strong style='color:#f8fafc;'>Navigation</strong><br>
        Use the pages in the sidebar above to explore all features.
    </div>
    """, unsafe_allow_html=True)

    # Agent status indicators
    st.markdown("### 🤖 Agent Status")
    agents = [
        ("🗓️ Planner", "Orchestrator"),
        ("🌤️ Weather", "Data Collection"),
        ("🏨 Hotels", "Recommendation"),
        ("✈️ Flights", "Intelligence"),
        ("💬 Reviews", "Sentiment"),
        ("💰 Budget", "Analytics"),
    ]
    for name, role in agents:
        st.markdown(f"""
        <div style='display:flex; justify-content:space-between; align-items:center;
                    padding:5px 8px; margin:2px 0; border-radius:6px;
                    background:rgba(22,33,62,0.6); font-size:0.8rem;'>
            <span style='color:#f8fafc;'>{name}</span>
            <span style='color:#10b981; font-size:0.7rem;'>● {role}</span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # Backend URL config
    with st.expander("⚙️ Settings"):
        backend_url = st.text_input(
            "Backend URL",
            value=st.session_state.backend_url,
            key="backend_url_input",
        )
        if backend_url != st.session_state.backend_url:
            st.session_state.backend_url = backend_url

        st.markdown(f"""
        <div style='font-size:0.75rem; color:#64748b; margin-top:8px;'>
            API Docs: <a href='{backend_url}/docs' target='_blank' style='color:#e94560;'>{backend_url}/docs</a>
        </div>
        """, unsafe_allow_html=True)

# ─── Main Home Page ───────────────────────────────────────────
st.markdown("""
<div class='destination-hero'>
    <h1>🌍 Agentic AI Travel Platform</h1>
    <p>Multi-agent AI-powered travel planning — smarter, faster, more personal</p>
</div>
""", unsafe_allow_html=True)

# Feature highlights
col1, col2, col3 = st.columns(3)
features = [
    ("🤖", "6 AI Agents", "Weather, Hotels, Flights, Reviews, Budget & Planning agents working in parallel"),
    ("⭐", "Travel Score", "Quantitative confidence score (0-100) computed from 5 weighted dimensions"),
    ("📄", "PDF Reports", "Professional travel reports generated and delivered via WhatsApp"),
    ("🌤️", "Weather Intel", "7-day forecasts with suitability scores and packing tips"),
    ("💬", "Review Analysis", "Sentiment analysis with pros/cons and recurring complaint detection"),
    ("👤", "Personalization", "Travel persona classification with adaptive tips and memory"),
]
cols = st.columns(3)
for i, (icon, title, desc) in enumerate(features):
    with cols[i % 3]:
        st.markdown(f"""
        <div class='metric-card'>
            <div style='font-size:2rem; margin-bottom:10px;'>{icon}</div>
            <div style='font-family: Space Grotesk, sans-serif; font-weight:700;
                        color:#f8fafc; font-size:1.05rem; margin-bottom:6px;'>{title}</div>
            <div style='font-size:0.82rem; color:#94a3b8; line-height:1.4;'>{desc}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("""
<div class='info-banner' style='margin-top:24px;'>
    <strong>🚀 Get Started:</strong> Navigate to <strong>🗺️ Plan Trip</strong> in the sidebar to begin your AI-powered travel planning journey.
    All 6 agents will run simultaneously to deliver your personalized plan in seconds.
</div>
""", unsafe_allow_html=True)

# Quick stats
st.markdown("### 📊 Platform Capabilities")
stat_col1, stat_col2, stat_col3, stat_col4 = st.columns(4)
with stat_col1:
    st.metric("AI Agents", "6", "Active")
with stat_col2:
    st.metric("Destinations", "10,000+", "Supported")
with stat_col3:
    st.metric("Data Points", "50+", "Per Trip")
with stat_col4:
    st.metric("Score Dimensions", "5", "Weighted")
