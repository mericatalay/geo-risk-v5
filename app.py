import streamlit as st
import pandas as pd
import time
import pydeck as pdk

from data import fetch_events
from model import calculate_risk_score

st.set_page_config(page_title="Analyst Intelligence Console", layout="wide")

# =========================
# 🧠 HEADER (EXEC STYLE)
# =========================
st.title("🧠 Analyst Intelligence Console v9")
st.caption("Systemic Risk & Geo-Political Analysis Layer")

# =========================
# 📡 DATA
# =========================
events = fetch_events()

if not events:
    st.error("⚠️ No data available")
    st.stop()

df = pd.DataFrame(events)

df["risk"] = df.apply(lambda x: calculate_risk_score(x), axis=1)

# =========================
# 🚨 GLOBAL RISK (OVERVIEW)
# =========================
avg_risk = df["risk"].mean()

if avg_risk > 7:
    status = "🔴 CRITICAL"
elif avg_risk > 4:
    status = "🟠 ELEVATED"
elif avg_risk > 2:
    status = "🟡 WATCH"
else:
    status = "🟢 STABLE"

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("System Status", status)

with col2:
    st.metric("Avg Risk", round(avg_risk, 2))

with col3:
    st.metric("Event Volume", len(df))

with col4:
    st.metric("Max Risk", int(df["risk"].max()))

# =========================
# 🧠 SYSTEMIC FACTORS (NEU)
# =========================
st.subheader("🧠 Systemic Pressure Indicators")

text_all = " ".join(df["title"].astype(str)).lower()

factors = {
    "Energy / Oil": ["oil", "energy", "gas", "petroleum"],
    "Shipping / Trade": ["shipping", "strait", "trade", "supply"],
    "Military Tension": ["war", "attack", "missile", "military", "strike"],
    "Political / Sanctions": ["sanctions", "political", "government", "diplomacy"]
}

factor_scores = {}

for k, keywords in factors.items():
    score = sum(any(word in t for word in keywords) for t in df["title"].astype(str).str.lower())
    factor_scores[k] = score

factor_df = pd.DataFrame({
    "Factor": list(factor_scores.keys()),
    "Pressure": list(factor_scores.values())
})

st.bar_chart(factor_df.set_index("Factor"))

# =========================
# 🌍 LOCATION ENGINE (SIMPLIFIED NLP)
# =========================
def extract_location(title):
    t = str(title).lower()

    if "iran" in t or "hormuz" in t or "gulf" in t:
        return [29.0, 52.0]
    elif "ukraine" in t or "russia" in t:
        return [49.0, 32.0]
    elif "china" in t or "taiwan" in t:
        return [23.5, 121.0]
    elif "europe" in t:
        return [50.0, 10.0]
    else:
        return [20.0, 0.0]


df["lat"] = df["title"].apply(lambda x: extract_location(x)[0])
df["lon"] = df["title"].apply(lambda x: extract_location(x)[1])

# =========================
# 🎨 COLOR MODEL
# =========================
df["color_r"] = (df["risk"] * 25).clip(0, 255)
df["color_g"] = 80
df["color_b"] = (255 - df["risk"] * 20).clip(0, 255)

# =========================
# 🗺️ MAP LAYERS
# =========================
heat_layer = pdk.Layer(
    "HeatmapLayer",
    data=df,
    get_position='[lon, lat]',
    get_weight="risk",
    radiusPixels=60
)

point_layer = pdk.Layer(
    "ScatterplotLayer",
    data=df,
    get_position='[lon, lat]',
    get_radius="risk * 20000",
    get_fill_color='[color_r, color_g, color_b]',
    pickable=True
)

view_state = pdk.ViewState(
    latitude=25,
    longitude=10,
    zoom=1.4
)

st.subheader("🌍 Global Risk Map")

st.pydeck_chart(pdk.Deck(
    layers=[heat_layer, point_layer],
    initial_view_state=view_state,
    tooltip={"text": "{title}\nRisk: {risk}"}
))

# =========================
# 📰 EXECUTIVE INTELLIGENCE FEED
# =========================
st.subheader("📰 Executive Intelligence Summary")

top = df.sort_values("risk", ascending=False).head(7)

for _, row in top.iterrows():
    emoji = "🔴" if row["risk"] > 7 else "🟠" if row["risk"] > 4 else "🟡"
    st.write(f"{emoji} {row.get('title', 'No title')}")

# =========================
# 🔁 REFRESH
# =========================
time.sleep(60)
st.rerun()