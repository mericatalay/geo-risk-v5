import streamlit as st
import pandas as pd
import time
import pydeck as pdk

from data import fetch_events
from model import calculate_risk_score

st.set_page_config(page_title="Geo Map Intelligence", layout="wide")

st.title("🌍 Geopolitical Map Intelligence")

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
# 🧠 STATUS (SIMPLE)
# =========================
avg_risk = df["risk"].mean()

status = "🟢 STABLE"
if avg_risk > 7:
    status = "🔴 HIGH RISK"
elif avg_risk > 4:
    status = "🟠 ELEVATED"
elif avg_risk > 2:
    status = "🟡 WATCH"

st.markdown(f"## Status: {status}")

st.progress(min(int(avg_risk * 10), 100))

# =========================
# 🌍 SIMPLE GEO MODEL
# =========================
def assign_region(title):
    t = str(title).lower()

    if "iran" in t or "hormuz" in t or "middle east" in t:
        return [32.0, 53.0]  # Iran / Gulf region
    elif "china" in t or "taiwan" in t:
        return [23.5, 121.0]
    elif "europe" in t:
        return [50.0, 10.0]
    else:
        return [20.0, 0.0]  # fallback global

df["coords"] = df["title"].apply(assign_region)
df["lat"] = df["coords"].apply(lambda x: x[0])
df["lon"] = df["coords"].apply(lambda x: x[1])

# =========================
# 🗺️ MAP LAYER
# =========================
layer = pdk.Layer(
    "ScatterplotLayer",
    data=df,
    get_position='[lon, lat]',
    get_radius="risk * 50000",
    get_fill_color=[
        "risk * 30",
        50,
        255 - "risk * 20"
    ],
    pickable=True
)

view_state = pdk.ViewState(
    latitude=30,
    longitude=20,
    zoom=1.5
)

st.pydeck_chart(pdk.Deck(
    layers=[layer],
    initial_view_state=view_state,
    tooltip={"text": "{title}\nRisk: {risk}"}
))

# =========================
# 📰 TOP EVENTS
# =========================
st.subheader("📰 Key Events")

top = df.sort_values("risk", ascending=False).head(5)

for _, row in top.iterrows():
    emoji = "🔴" if row["risk"] > 7 else "🟠" if row["risk"] > 4 else "🟡"
    st.write(f"{emoji} {row.get('title','No title')}")

# =========================
# 🔁 REFRESH
# =========================
time.sleep(60)
st.rerun()