import streamlit as st
import pandas as pd
import time
import pydeck as pdk
import feedparser

# =========================
# 🌐 LANGUAGE
# =========================
lang = st.sidebar.selectbox("Language / Sprache / Dil",
                            ["Deutsch", "English", "Türkçe"])

def T(de, en, tr=None):
    return de if lang == "Deutsch" else en if lang == "English" else (tr or en)

# =========================
# PAGE
# =========================
st.set_page_config(page_title="Meric Intel v19", layout="wide")

st.title("🧭 Meric’s Intel v19")
st.caption("OSINT + Economic + Cascading Risk + PONR System")

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
    } for e in feed.entries[:10]]

df = pd.DataFrame(sum([load(r) for r in RSS], []))

if df.empty:
    st.error("No data")
    st.stop()

# =========================
# RISK ENGINE
# =========================
def risk(t):
    t = str(t).lower()
    score = 1
    keys = {
        "war": 3, "attack": 3,
        "oil": 3, "gas": 2,
        "shipping": 3,
        "iran": 4, "china": 3, "russia": 3
    }
    for k, v in keys.items():
        if k in t:
            score += v
    return min(score, 10)

df["risk"] = df["title"].apply(risk)

system_score = min(100, df["risk"].mean() * 10)

# =========================
# 📊 HEADER (COMPACT)
# =========================
c1, c2, c3 = st.columns(3)

c1.metric("System Risk", round(system_score, 1))
c2.metric("Events", len(df))
c3.metric("State", "Active Monitoring")

# =========================
# 🧭 PONR MODEL (NEW CORE)
# =========================
def ponr(value):
    if value <= 40:
        return ("🟢 Stable", 20)
    elif value <= 60:
        return ("🟡 Early Instability", 45)
    elif value <= 75:
        return ("🟠 Critical Pressure", 65)
    elif value <= 90:
        return ("🔴 Near PONR", 85)
    else:
        return ("⚫ PONR Zone", 100)

ponr_label, ponr_index = ponr(system_score)

# =========================
# 🌍 LOCATION
# =========================
def location(t):
    t = str(t).lower()
    if "iran" in t:
        return [29, 52]
    if "ukraine" in t:
        return [49, 32]
    if "china" in t:
        return [23, 121]
    return [20, 0]

df["lat"] = df["title"].apply(lambda x: location(x)[0])
df["lon"] = df["title"].apply(lambda x: location(x)[1])

# =========================
# 🗺️ MAP (SMALL)
# =========================
df["color_r"] = (df["risk"] * 20).clip(0, 255)
df["color_g"] = 80
df["color_b"] = (255 - df["risk"] * 15).clip(0, 255)

st.subheader("🌍 Situation Map")

layer = pdk.Layer(
    "ScatterplotLayer",
    data=df,
    get_position='[lon, lat]',
    get_radius="risk * 11000",
    get_fill_color='[color_r, color_g, color_b]',
    pickable=True
)

st.pydeck_chart(pdk.Deck(
    layers=[layer],
    initial_view_state=pdk.ViewState(25, 10, 1.2),
    height=300,
    tooltip={"text": "{title}\nRisk: {risk}"}
))

# =========================
# 🧠 PONR DISPLAY (KEY FEATURE)
# =========================
st.subheader("⚠️ Point of No Return (PONR) Indicator")

st.metric("PONR Status", ponr_label)
st.progress(ponr_index / 100)

st.caption(
    "PONR measures system controllability. Above 75 = self-reinforcing cascade risk."
)

# =========================
# 🌊 CASCADING MODEL (WITH LEVELS)
# =========================
st.subheader("🌊 Cascading Risk Model")

def cascade_level(score):
    if score < 25:
        return "🟢 Stable"
    elif score < 45:
        return "🟡 Pressure"
    elif score < 65:
        return "🟠 Active Cascade"
    elif score < 85:
        return "🔴 System Reinforcement"
    return "⚫ Near PONR"

energy = df["title"].str.contains("oil|gas|energy", case=False, na=False).mean() * 100
trade = df["title"].str.contains("shipping|trade", case=False, na=False).mean() * 100
conflict = df["title"].str.contains("war|attack|military", case=False, na=False).mean() * 100

st.write("🔋 Energy:", cascade_level(energy))
st.write("🚢 Trade:", cascade_level(trade))
st.write("🪖 Conflict:", cascade_level(conflict))

# =========================
# 🌍 ECONOMIC PRESSURE (EXPLAINED)
# =========================
st.subheader("🌍 Economic Pressure Index (Explained)")

def econ_label(v):
    if v <= 25:
        return "🟢 Normal"
    elif v <= 45:
        return "🟡 Early Stress"
    elif v <= 65:
        return "🟠 Inflation Pressure"
    elif v <= 80:
        return "🔴 System Stress"
    return "⚫ Shock Zone"

col1, col2, col3 = st.columns(3)

col1.metric("Energy", econ_label(energy))
col2.metric("Trade", econ_label(trade))
col3.metric("Conflict", econ_label(conflict))

st.caption("0–25 normal | 25–45 early stress | 45–65 inflation pressure | 65–80 systemic stress | 80+ shock zone")

# =========================
# 📰 INTELLIGENCE FEED
# =========================
st.subheader("📰 Intelligence Feed")

for _, r in df.sort_values("risk", ascending=False).head(10).iterrows():
    st.markdown(f"🔴 [{r['title']}]({r['link']})")

# =========================
# 🚨 CRISIS HUB
# =========================
st.subheader("🚨 Crisis Hub")

top = df.sort_values("risk", ascending=False).head(3)

for _, r in top.iterrows():
    st.write("🔥", r["title"])

# =========================
# 🔁 REFRESH
# =========================
time.sleep(60)
st.rerun()