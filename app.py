import streamlit as st
import pandas as pd
import feedparser
import pydeck as pdk
import time

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(page_title="Intel v30", layout="wide")

# =========================
# TRUE DARK MODE FIX
# =========================
st.markdown("""
<style>
body {
    background-color: #000000 !important;
    color: #ffffff !important;
}

.block-container {
    padding-top: 0.4rem;
    background-color: #000000;
}

div[data-testid="stMetric"] {
    background-color: #0b0b0b;
    border: 1px solid #1a1a1a;
    padding: 10px;
    border-radius: 6px;
}

.stProgress > div > div > div > div {
    background-color: #4a90e2;
}
</style>
""", unsafe_allow_html=True)

st.title("🧭 Intel Command v30")
st.caption("Full Fix • Dark Mode • Map Restored • Compact Intelligence System")

# =========================
# DATA
# =========================
RSS = [
    "https://feeds.bbci.co.uk/news/world/rss.xml",
    "https://www.aljazeera.com/xml/rss/all.xml"
]

def load(url):
    feed = feedparser.parse(url)
    return [{
        "title": e.get("title"),
        "link": e.get("link")
    } for e in feed.entries[:15]]

df = pd.DataFrame(sum([load(r) for r in RSS], []))

if df.empty:
    st.error("No data available")
    st.stop()

# =========================
# RISK ENGINE
# =========================
def score(col, keywords):
    return col.str.contains("|".join(keywords), case=False, na=False).mean() * 10

energy = score(df["title"], ["oil", "gas", "energy"])
geo = score(df["title"], ["war", "attack", "military", "russia", "china", "iran"])
finance = score(df["title"], ["inflation", "bank", "market", "rate"])
supply = score(df["title"], ["shipping", "trade", "port", "supply"])
ukraine = score(df["title"], ["ukraine", "kyiv", "front", "russia"])

system_risk = df["title"].str.contains("war|attack|oil|gas", case=False, na=False).mean() * 10

cascade = (energy + geo + finance + supply + ukraine) / 5
ponr = (system_risk + cascade) / 2

# =========================
# SCENARIOS
# =========================
worst = ponr * 9
stable = max(0, 100 - worst - 10)
deesc = max(0, 100 - worst - 20)

total = worst + stable + deesc

scenarios = {
    "Worst Case": worst / total * 100,
    "Status Quo": stable / total * 100,
    "De-escalation": deesc / total * 100
}

active = max(scenarios, key=scenarios.get)

# =========================
# HEADER
# =========================
st.markdown("## 🧠 Global Intelligence Overview")
st.markdown(f"### 🔮 Active Scenario: **{active}**")

c1, c2, c3, c4 = st.columns(4)
c1.metric("System Risk", round(system_risk, 2))
c2.metric("Cascade", round(cascade, 2))
c3.metric("PONR", round(ponr, 2))
c4.metric("Events", len(df))

st.progress(ponr / 10)

# =========================
# MAP (RESTORED)
# =========================
def location(t):
    t = str(t).lower()
    if "ukraine" in t or "kyiv" in t: return [49, 32]
    if "russia" in t: return [60, 90]
    if "iran" in t: return [32, 53]
    if "china" in t: return [35, 103]
    if "israel" in t or "gaza" in t: return [31, 35]
    return [20, 0]

df["lat"] = df["title"].apply(lambda x: location(x)[0])
df["lon"] = df["title"].apply(lambda x: location(x)[1])
df["risk"] = df["title"].str.contains("war|attack|oil|gas|russia|china|iran", case=False, na=False).astype(int) * 5 + 2

st.markdown("## 🌍 Crisis Map")

layer = pdk.Layer(
    "ScatterplotLayer",
    data=df,
    get_position='[lon, lat]',
    get_radius="risk * 5000",
    get_fill_color='[255, 80, 80, 160]',
    pickable=True
)

st.pydeck_chart(pdk.Deck(
    layers=[layer],
    initial_view_state=pdk.ViewState(
        latitude=30,
        longitude=20,
        zoom=1.3
    ),
    height=320
))

# =========================
# SYSTEM BARS (COMPACT)
# =========================
st.markdown("## 📊 System Stress (0–10)")

col1, col2 = st.columns(2)

with col1:
    st.progress(energy / 10)
    st.caption(f"🛢 Energy: {energy:.1f}")

    st.progress(geo / 10)
    st.caption(f"🪖 Geo: {geo:.1f}")

    st.progress(finance / 10)
    st.caption(f"💰 Finance: {finance:.1f}")

with col2:
    st.progress(supply / 10)
    st.caption(f"🚢 Supply: {supply:.1f}")

    st.progress(ukraine / 10)
    st.caption(f"🇺🇦 Ukraine: {ukraine:.1f}")

# =========================
# SCENARIOS
# =========================
st.markdown("## 🔮 Scenario Forecast")

sc1, sc2, sc3 = st.columns(3)
sc1.metric("🔴 Worst", f"{scenarios['Worst Case']:.1f}%")
sc2.metric("🟡 Stable", f"{scenarios['Status Quo']:.1f}%")
sc3.metric("🟢 De-escalation", f"{scenarios['De-escalation']:.1f}%")

# =========================
# FEED
# =========================
st.markdown("## 🧠 Intelligence Feed")

for _, r in df.head(10).iterrows():
    st.markdown(f"""
    <div style="
        background:#0b0b0b;
        border:1px solid #1a1a1a;
        padding:6px;
        border-radius:6px;
        margin-bottom:4px;
        font-size:11px;">
        🔹 <a href="{r['link']}" target="_blank" style="color:white;text-decoration:none;">
        {r['title']}</a>
    </div>
    """, unsafe_allow_html=True)

# =========================
# FOOTER LOGIC
# =========================
st.markdown("---")

with st.expander("🧠 System Logic"):
    st.write("""
    - Dark mode restored
    - Map restored (pydeck)
    - Compact bars instead of charts
    - Scenario + PONR retained
    - Balanced single-screen layout
    """)

# =========================
# REFRESH
# =========================
time.sleep(60)
st.rerun()