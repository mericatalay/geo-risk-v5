import streamlit as st
import pandas as pd
import feedparser
import time

# =========================
# CONFIG (COMPACT INTEL UI)
# =========================
st.set_page_config(page_title="Intel v29", layout="wide")

st.markdown("""
<style>
body { background-color: #000; color: #fff; }

.block-container { padding-top: 0.3rem; }

.panel {
    background-color: #0b0b0b;
    border: 1px solid #1a1a1a;
    padding: 6px;
    border-radius: 6px;
    margin-bottom: 4px;
    font-size: 11px;
}

.small { font-size: 11px; }
</style>
""", unsafe_allow_html=True)

st.title("🧭 Intel Command v29")
st.caption("Compact Intelligence Layout • Single Screen OSINT View")

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
    } for e in feed.entries[:12]]

df = pd.DataFrame(sum([load(r) for r in RSS], []))

if df.empty:
    st.error("No data")
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
# SCENARIOS (LIGHT VERSION)
# =========================
worst = ponr * 9
stable = max(0, 100 - worst - 10)
deesc = max(0, 100 - worst - 20)

total = worst + stable + deesc

scenarios = {
    "Worst": worst / total * 100,
    "Stable": stable / total * 100,
    "De-escalation": deesc / total * 100
}

active = max(scenarios, key=scenarios.get)

# =========================
# HEADER (ONE SCREEN FOCUS)
# =========================
st.markdown("## 🧠 Forecast")
st.markdown(f"### 🔮 {active}")

c1, c2, c3, c4 = st.columns(4)
c1.metric("Risk", round(system_risk, 2))
c2.metric("Cascade", round(cascade, 2))
c3.metric("PONR", round(ponr, 2))
c4.metric("Events", len(df))

st.progress(ponr / 10)

# =========================
# COMPACT BARS (KEY UPGRADE)
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
# SCENARIOS COMPACT
# =========================
st.markdown("## 🔮 Scenario Split")

sc1, sc2, sc3 = st.columns(3)

sc1.metric("🔴 Worst", f"{scenarios['Worst']:.1f}%")
sc2.metric("🟡 Stable", f"{scenarios['Stable']:.1f}%")
sc3.metric("🟢 De-escalation", f"{scenarios['De-escalation']:.1f}%")

# =========================
# FEED (COMPACT LIST)
# =========================
st.markdown("## 🧠 Intelligence Feed")

for _, r in df.head(8).iterrows():
    st.markdown(f"""
    <div class="panel">
    🔹 <a href="{r['link']}" target="_blank" style="color:white;text-decoration:none;">
    {r['title']}</a>
    </div>
    """, unsafe_allow_html=True)

# =========================
# FOOTER LOGIC
# =========================
st.markdown("---")

with st.expander("🧠 System Logic (Compact Model)"):
    st.write("""
    - All indicators are normalized 0–10
    - PONR = blended systemic stress index
    - Cascade = interdependence of global systems
    - Scenario split = probability-weighted stress outcomes
    - Design optimized for single-screen monitoring
    """)

# =========================
# REFRESH
# =========================
time.sleep(60)
st.rerun()