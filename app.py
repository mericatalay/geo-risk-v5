import streamlit as st
import pandas as pd
import time
import pydeck as pdk

from data import fetch_events
from model import calculate_risk_score

# =========================
# 🌐 LANGUAGE
# =========================
lang = st.sidebar.selectbox("Language / Sprache / Dil",
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
st.set_page_config(page_title="Analyst v14", layout="wide")

st.title(T(
    "🧠 Analyst v14 – Cascading Risk Intelligence",
    "🧠 Analyst v14 – Cascading Risk Intelligence",
    "🧠 Analist v14 – Zincirleme Risk Sistemi"
))

# =========================
# DATA
# =========================
events = fetch_events()

if not events:
    st.error("No data")
    st.stop()

df = pd.DataFrame(events)
df["risk"] = df.apply(lambda x: calculate_risk_score(x), axis=1)

# =========================
# 🌍 LOCATION
# =========================
def location(t):
    t = str(t).lower()

    if "iran" in t or "hormuz" in t:
        return [29, 52]
    elif "ukraine" in t or "russia" in t:
        return [49, 32]
    elif "china" in t or "taiwan" in t:
        return [23, 121]
    else:
        return [20, 0]

df["lat"] = df["title"].apply(lambda x: location(x)[0])
df["lon"] = df["title"].apply(lambda x: location(x)[1])

# =========================
# 🧠 SYSTEM SCORE
# =========================
avg_risk = df["risk"].mean()
trend = df["risk"].tail(5).mean() - avg_risk

# =========================
# ⚠️ HUMAN READABLE SCALE
# =========================
def risk_label(v):
    if v <= 20:
        return "🟢 Stable"
    elif v <= 40:
        return "🟡 Watch"
    elif v <= 60:
        return "🟠 Stress"
    elif v <= 80:
        return "🔴 Escalation"
    else:
        return "⚫ Crisis"

system_score = min(100, avg_risk * 10)

# =========================
# 📊 HEADER KPI
# =========================
c1, c2, c3, c4 = st.columns(4)

c1.metric("System Risk", risk_label(system_score))
c2.metric("Score", round(system_score, 1))
c3.metric("Trend", round(trend, 2))
c4.metric("Events", len(df))

# =========================
# 🗺️ MAP
# =========================
df["color_r"] = (df["risk"] * 25).clip(0, 255)
df["color_g"] = 80
df["color_b"] = (255 - df["risk"] * 20).clip(0, 255)

heat = pdk.Layer(
    "HeatmapLayer",
    data=df,
    get_position='[lon, lat]',
    get_weight="risk",
    radiusPixels=60
)

points = pdk.Layer(
    "ScatterplotLayer",
    data=df,
    get_position='[lon, lat]',
    get_radius="risk * 20000",
    get_fill_color='[color_r, color_g, color_b]',
    pickable=True
)

st.subheader("🌍 Global Risk Map")

st.pydeck_chart(pdk.Deck(
    layers=[heat, points],
    initial_view_state=pdk.ViewState(latitude=25, longitude=10, zoom=1.4),
    tooltip={"text": "{title}\nRisk: {risk}"}
))

# =========================
# ⏱️ CASCADING FORECAST ENGINE
# =========================
st.subheader("⏱️ Cascading Timeline Forecast")

now_risk = system_score
short = now_risk + trend * 5
mid = now_risk + trend * 10
long = now_risk + trend * 15

col1, col2, col3, col4 = st.columns(4)

col1.metric("NOW (0–72h)", risk_label(now_risk))
col2.metric("SHORT (3–14d)", risk_label(short))
col3.metric("MID (2–8w)", risk_label(mid))
col4.metric("LONG (2–12m)", risk_label(long))

st.caption("Risk progression shows potential cascade amplification over time")

# =========================
# 🌊 CASCADING EFFECTS (EXPLAINER)
# =========================
st.subheader("🌊 Potential Cascade Effects")

energy = df[df["title"].str.contains("oil|gas|energy", case=False, na=False)]["risk"].mean()
shipping = df[df["title"].str.contains("shipping|strait|trade", case=False, na=False)]["risk"].mean()
agri = df[df["title"].str.contains("fertilizer|grain|wheat|food", case=False, na=False)]["risk"].mean()

st.write("🔋 Energy System Pressure:", risk_label(min(100, energy * 10)))
st.write("🚢 Supply Chain Pressure:", risk_label(min(100, shipping * 10)))
st.write("🌾 Agricultural Pressure:", risk_label(min(100, agri * 10)))

st.caption("These are systemic dependency indicators (energy → inflation → food security)")

# =========================
# 🚨 ALERT ENGINE
# =========================
st.subheader("🚨 Alert Engine")

alerts = []

if system_score > 75:
    alerts.append("⚫ Systemic instability increasing")
if trend > 2:
    alerts.append("⚠️ Rapid escalation detected")
if shipping > 5:
    alerts.append("🚢 Global trade stress rising")
if energy > 5:
    alerts.append("🔋 Energy market pressure increasing")

if alerts:
    for a in alerts:
        st.write(a)
else:
    st.write("🟢 No critical alerts")

# =========================
# 🔁 REFRESH
# =========================
time.sleep(60)
st.rerun()