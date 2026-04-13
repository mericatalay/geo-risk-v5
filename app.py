import streamlit as st
import pandas as pd
import time
import pydeck as pdk

from data import fetch_events
from model import calculate_risk_score

st.set_page_config(page_title="True Intelligence Map", layout="wide")

st.title("🌍 True Intelligence Map (Cognitive OSINT View)")

# =========================
# 📡 DATA
# =========================
events = fetch_events()

if not events:
    st.error("⚠️ No data available")
    st.stop()

df = pd.DataFrame(events)

# =========================
# 🧠 RISK SCORING
# =========================
df["risk"] = df.apply(lambda x: calculate_risk_score(x), axis=1)

# =========================
# 🚨 GLOBAL STATUS (Cognitive UI)
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

st.markdown(f"## System Status: {status}")
st.progress(min(int(avg_risk * 10), 100))

# =========================
# 🌍 LOCATION (simple extraction fallback)
# =========================
def extract_location(title):
    t = str(title).lower()

    if "iran" in t or "hormuz" in t or "gulf" in t:
        return [29.0, 52.0]   # Middle East
    elif "china" in t or "taiwan" in t:
        return [23.5, 121.0]
    elif "ukraine" in t or "russia" in t:
        return [49.0, 32.0]
    elif "europe" in t:
        return [50.0, 10.0]
    else:
        return [20.0, 0.0]  # global fallback


df["lat"] = df["title"].apply(lambda x: extract_location(x)[0])
df["lon"] = df["title"].apply(lambda x: extract_location(x)[1])

# =========================
# 🎨 COLOR FIX (IMPORTANT!)
# =========================
df["color_r"] = (df["risk"] * 25).clip(0, 255)
df["color_g"] = 80
df["color_b"] = (255 - df["risk"] * 20).clip(0, 255)

# =========================
# 🗺️ HEATMAP LAYER
# =========================
heat_layer = pdk.Layer(
    "HeatmapLayer",
    data=df,
    get_position='[lon, lat]',
    get_weight="risk",
    radiusPixels=60
)

# =========================
# 🔴 POINT LAYER (FIXED)
# =========================
point_layer = pdk.Layer(
    "ScatterplotLayer",
    data=df,
    get_position='[lon, lat]',
    get_radius="risk * 20000",
    get_fill_color='[color_r, color_g, color_b]',
    pickable=True
)

# =========================
# 🌍 VIEW SETTINGS
# =========================
view_state = pdk.ViewState(
    latitude=25,
    longitude=10,
    zoom=1.4
)

# =========================
# 🗺️ MAP RENDER
# =========================
st.pydeck_chart(pdk.Deck(
    layers=[heat_layer, point_layer],
    initial_view_state=view_state,
    tooltip={"text": "{title}\nRisk: {risk}"}
))

# =========================
# 📰 TOP EVENTS (Cognitive Feed)
# =========================
st.subheader("📰 Key Intelligence Events")

top = df.sort_values("risk", ascending=False).head(5)

for _, row in top.iterrows():
    emoji = "🔴" if row["risk"] > 7 else "🟠" if row["risk"] > 4 else "🟡"
    st.write(f"{emoji} {row.get('title', 'No title')}")

# =========================
# 🔁 AUTO REFRESH
# =========================
time.sleep(60)
st.rerun()