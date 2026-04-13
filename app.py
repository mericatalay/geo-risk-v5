import streamlit as st
import pandas as pd
import time
import pydeck as pdk
import feedparser

# =========================
# 🌐 LANGUAGE
# =========================
lang = st.sidebar.selectbox("Language / Dil / Sprache",
                            ["Deutsch", "English", "Türkçe"])

def T(de, en, tr=None):
    if lang == "Deutsch":
        return de
    elif lang == "English":
        return en
    elif lang == "Türkçe":
        return tr if tr else en
    return en

# =========================
# PAGE
# =========================
st.set_page_config(page_title="Meric Analyst v16", layout="wide")

st.title("🧭 Meric’s Analyst Tool v16")
st.caption("Situation Room – Multi-Source Intelligence System")

# =========================
# 📰 RSS INGESTION (MULTI SOURCE)
# =========================
RSS_FEEDS = {
    "West": [
        "https://feeds.bbci.co.uk/news/world/rss.xml",
    ],
    "Global": [
        "https://www.aljazeera.com/xml/rss/all.xml",
    ]
}

def load_feed(url, source_tag):
    feed = feedparser.parse(url)
    items = []
    for e in feed.entries[:10]:
        items.append({
            "title": e.get("title", ""),
            "source": source_tag
        })
    return items

events = []
for src, feeds in RSS_FEEDS.items():
    for f in feeds:
        events += load_feed(f, src)

df = pd.DataFrame(events)

if df.empty:
    st.error("No live data")
    st.stop()

# =========================
# 🧠 SIMPLE RISK ENGINE
# =========================
def risk_score(text):
    t = str(text).lower()
    score = 1
    keywords = {
        "war": 3, "attack": 3, "missile": 4,
        "oil": 3, "gas": 2, "shipping": 3,
        "iran": 4, "china": 3, "russia": 3
    }
    for k, v in keywords.items():
        if k in t:
            score += v
    return min(score, 10)

df["risk"] = df["title"].apply(risk_score)

# =========================
# 🌍 LOCATION ENGINE
# =========================
def location(t):
    t = str(t).lower()
    if "iran" in t or "hormuz" in t:
        return [29, 52]
    elif "ukraine" in t or "russia" in t:
        return [49, 32]
    elif "china" in t:
        return [23, 121]
    return [20, 0]

df["lat"] = df["title"].apply(lambda x: location(x)[0])
df["lon"] = df["title"].apply(lambda x: location(x)[1])

# =========================
# 🧠 SYSTEM SCORE
# =========================
avg_risk = df["risk"].mean()
trend = df["risk"].tail(5).mean() - avg_risk
system_score = min(100, avg_risk * 10)

# =========================
# 🚨 HUMAN SCALE
# =========================
def label(v):
    if v < 20:
        return "🟢 Stable"
    elif v < 40:
        return "🟡 Watch"
    elif v < 60:
        return "🟠 Stress"
    elif v < 80:
        return "🔴 Escalation"
    return "⚫ Crisis"

# =========================
# 📊 HEADER
# =========================
c1, c2, c3, c4 = st.columns(4)

c1.metric("System", label(system_score))
c2.metric("Risk", round(system_score, 1))
c3.metric("Trend", round(trend, 2))
c4.metric("Events", len(df))

# =========================
# 🧠 CRISIS CLUSTER NAME
# =========================
def crisis_name(df):
    text = " ".join(df["title"].astype(str)).lower()

    if "hormuz" in text or "iran" in text:
        return "Hormuz Pressure Event"
    if "ukraine" in text or "russia" in text:
        return "Black Sea Security Stress"
    if "china" in text:
        return "Asia-Pacific Tension Cluster"
    return "Global Stability Pressure"

# =========================
# 🗺️ MAP (SMALL & CLEAN)
# =========================
df["color_r"] = (df["risk"] * 20).clip(0, 255)
df["color_g"] = 80
df["color_b"] = (255 - df["risk"] * 15).clip(0, 255)

st.subheader("🌍 Situation Map")

heat = pdk.Layer(
    "HeatmapLayer",
    data=df,
    get_position='[lon, lat]',
    get_weight="risk",
    radiusPixels=45
)

points = pdk.Layer(
    "ScatterplotLayer",
    data=df,
    get_position='[lon, lat]',
    get_radius="risk * 12000",
    get_fill_color='[color_r, color_g, color_b]',
    pickable=True
)

st.pydeck_chart(pdk.Deck(
    layers=[heat, points],
    initial_view_state=pdk.ViewState(latitude=25, longitude=10, zoom=1.2),
    height=320,
    tooltip={"text": "{title}\nRisk: {risk}"}
))

# =========================
# 🧠 AI SUMMARY (NEW CORE)
# =========================
st.subheader("🧠 AI Situation Summary")

st.info(
    f"""
**Current Crisis Frame:** {crisis_name(df)}

**What is happening?**  
Multiple geopolitical and supply-chain stress signals are active across regions.

**Why it matters:**  
Persistent stress increases probability of cascading effects (energy → trade → inflation → food systems).

**Direction:**  
{"Escalation pressure increasing" if trend > 1 else "Stable but fragile conditions"}
"""
)

# =========================
# 🌊 CASCADE VIEW
# =========================
st.subheader("🌊 Cascading Risk Model")

st.write("🔋 Energy → Inflation → Food Security")
st.write("🚢 Shipping → Supply Chain Delay")
st.write("🪖 Conflict → Trade Disruption → Energy Shock")

# =========================
# 📰 MULTI SOURCE FEED
# =========================
st.subheader("📰 Multi-Source Intelligence Feed")

col1, col2 = st.columns(2)

west = df[df["source"] == "West"].head(5)
global_src = df[df["source"] == "Global"].head(5)

with col1:
    st.markdown("### 🌐 Western View")
    for _, r in west.iterrows():
        st.write("🟦", r["title"])

with col2:
    st.markdown("### 🌏 Global View")
    for _, r in global_src.iterrows():
        st.write("🟩", r["title"])

# =========================
# 🚨 CRISIS PANEL
# =========================
st.subheader("🚨 Crisis Hub")

st.error(crisis_name(df))

top = df.sort_values("risk", ascending=False).head(3)
for _, r in top.iterrows():
    st.write("🔥", r["title"])

# =========================
# 🔁 LOOP
# =========================
time.sleep(60)
st.rerun()