"""
Page 2: Hotel Recommendations & Attractions
Ranked horizontal image cards with AI reasoning.
"""
import streamlit as st
from pathlib import Path

st.set_page_config(page_title="Recommendations | AI Travel", page_icon="🏨", layout="wide")

css_path = Path(__file__).parent.parent / "assets" / "style.css"
if css_path.exists():
    with open(css_path, encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
.stApp { background: linear-gradient(135deg, #0f0c29 0%, #1a1a2e 40%, #16213e 100%); color: #f8fafc; font-family: 'Inter', sans-serif;}
section[data-testid="stSidebar"] { background: linear-gradient(180deg, #0f0c29, #1a1a2e); }
h1,h2,h3 { color: #f8fafc; font-family: 'Space Grotesk', sans-serif; }
p, label, span { color: #cbd5e1; }

.horizontal-scroll-container {
    display: flex;
    overflow-x: auto;
    gap: 20px;
    padding: 10px 0 20px 0;
    scroll-snap-type: x mandatory;
}
.horizontal-scroll-container::-webkit-scrollbar {
    height: 8px;
}
.horizontal-scroll-container::-webkit-scrollbar-thumb {
    background: #334155;
    border-radius: 4px;
}
.image-card {
    min-width: 320px;
    max-width: 320px;
    background: #1e293b;
    border-radius: 16px;
    border: 1px solid rgba(255,255,255,0.05);
    overflow: hidden;
    scroll-snap-align: start;
    flex-shrink: 0;
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


result = st.session_state.get("trip_result")

if not result:
    st.warning("⚠️ No trip planned yet. Go to **🗺️ Plan Trip** to get started.")
    st.stop()

hotels = result.get("recommended_hotels", [])
attractions = result.get("attractions", [])
destination = result.get("destination", "")

# ─── Ranked Accommodations ──────────────────────────────────────
st.markdown("### Ranked Accommodations")
st.markdown(f"<p style='font-size:0.9rem; color:#94a3b8; margin-top:-10px; margin-bottom:15px;'>Based on your preferences for luxury and location in {destination}</p>", unsafe_allow_html=True)

if not hotels:
    st.info("No accommodations found.")
else:
    cards_html = "<div class='horizontal-scroll-container'>"
    for h in hotels:
        name = h.get("hotel_name", "Hotel")
        price = h.get("price_per_night_usd", 0)
        img_url = h.get("image_url") or f"https://picsum.photos/seed/{abs(hash(name))}/800/500"
        badge = h.get("rank_badge") or "#1 Pick"
        reasoning = h.get("ai_reasoning") or "Highly rated by guests for location and amenities."
        
        tags_html = ""
        for i, tag in enumerate(h.get("amenities", [])[:3]):
            tags_html += f"<span class='card-tag'>{tag}</span>"
            
        cards_html += f"""
<div class='image-card'>
    <div class='card-image-container'>
        <div class='card-badge'>{badge}</div>
        <img src='{img_url}' alt='{name}'>
    </div>
    <div class='card-content'>
        <div class='card-title-row'>
            <div class='card-title' title='{name}'>{name}</div>
            <div class='card-price'>${price:.0f}/night</div>
        </div>
        <div class='card-tags'>
            {tags_html}
        </div>
    </div>
    <div class='card-ai-reasoning'>
        <div class='card-ai-reasoning-title'>✨ AI Why Recommended:</div>
        <div class='card-ai-reasoning-text'>{reasoning}</div>
    </div>
</div>
"""
    cards_html += "</div>"
    st.markdown(cards_html, unsafe_allow_html=True)


st.markdown("<br><br>", unsafe_allow_html=True)


# ─── Top Attractions ────────────────────────────────────────────
st.markdown("### Top Attractions")
st.markdown(f"<p style='font-size:0.9rem; color:#94a3b8; margin-top:-10px; margin-bottom:15px;'>Curated itinerary highlights for {destination}</p>", unsafe_allow_html=True)

if not attractions:
    st.info("No attractions found.")
else:
    attr_cards_html = "<div class='horizontal-scroll-container'>"
    for i, a in enumerate(attractions):
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
            
        attr_cards_html += f"""
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
    attr_cards_html += "</div>"
    st.markdown(attr_cards_html, unsafe_allow_html=True)
