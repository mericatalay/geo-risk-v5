import streamlit as st
import pandas as pd
import time
import pydeck as pdk

from data import fetch_events
from model import calculate_risk_score

# =========================
# 🌐 LANGUAGE SYSTEM
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
# PAGE CONFIG
# =========================
st.set_page_config(page_title="Analyst v13", layout="wide")

st.title(T("🧠 Analyst v13 – Command Layout",
           "🧠 Analyst v13 – Command Layout",
           "🧠 Analist v13 – Komuta Paneli"))

# =========================
# DATA
# =========================
events = fetch_events()

if not events:
    st.error(T("Keine Daten", "No data", "Veri yok"))
    st.stop()

df = pd.DataFrame(events)
df["risk"] = df.apply(lambda x: calculate_risk_score(x), axis=1)

# =========================
# 🧠 LOCATION ENGINE
# =========================
def location(text):
    t = str(text).lower()

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
# 🧠 SYSTEM STATUS
# =========================
avg_risk = df["risk"].mean()
trend = df["risk"].tail(5).mean() - avg_risk

if avg_risk > 7:
    status = "🔴 CRITICAL"
elif avg_risk > 4:
    status = "🟠 ELEVATED"
elif avg_risk > 2:
    status = "🟡 WATCH"
else:
    status = "🟢 STABLE"

# =========================
# 📊 KPI HEADER
# =========================
c1, c2, c3, c4 = st.columns(4)

c1.metric("Status", status)
c2.metric("Avg Risk", round(avg_risk, 2))
c3.metric("Trend", round(trend, 2))
c4.metric("Events", len(df))

# =========================
# 🗺️ TOP MAP (FULL WIDTH)
# =========================
st.subheader(T("🌍 Globale Lagekarte",
               "🌍 Global Situation Map",
               "🌍 Küresel Durum Haritası"))

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

view = pdk.ViewState(latitude=25, longitude=10, zoom=1.4)

st.pydeck_chart(pdk.Deck(
    layers=[heat, points],
    initial_view_state=view,
    tooltip={"text": "{title}\nRisk: {risk}"}
))

# =========================
# 📦 LOWER LAYOUT SPLIT
# =========================
left, right = st.columns([2, 1])

# =========================
# 🧩 LEFT: CLUSTERS + FEED
# =========================
with left:
    st.subheader(T("🧩 Risiko Cluster", "Risk Clusters", "Risk Grupları"))

    def cluster(text):
        t = str(text).lower()
        if any(x in t for x in ["oil", "gas", "energy"]):
            return "Energy"
        elif any(x in t for x in ["war", "attack", "military"]):
            return "Military"
        elif any(x in t for x in ["trade", "shipping", "strait"]):
            return "Trade"
        else:
            return "General"

    df["cluster"] = df["title"].apply(cluster)

    st.bar_chart(df.groupby("cluster")["risk"].mean())

    st.subheader(T("📰 Intelligence Feed",
                   "Intelligence Feed",
                   "İstihbarat Akışı"))

    top = df.sort_values("risk", ascending=False).head(7)

    for _, row in top.iterrows():
        emoji = "🔴" if row["risk"] > 7 else "🟠" if row["risk"] > 4 else "🟡"
        st.write(f"{emoji} [{row['cluster']}] {row.get('title','No title')}")

# =========================
# 📈 RIGHT TOP: FORECAST ENGINE
# =========================
with right:
    st.subheader(T("📈 Forecast Engine",
                   "Forecast Engine",
                   "Tahmin Motoru"))

    if len(df) > 5:
        recent = df["risk"].tail(5).mean()
        base = df["risk"].mean()

        delta = recent - base

        forecast_7d = avg_risk + (delta * 2)
        forecast_14d = avg_risk + (delta * 3)

        st.metric("7D Forecast", round(forecast_7d, 2))
        st.metric("14D Forecast", round(forecast_14d, 2))
    else:
        st.write("Not enough data")

# =========================
# 🚨 RIGHT BOTTOM: ALERT ENGINE
# =========================
with right:
    st.subheader(T("🚨 Alert Engine",
                   "Alert Engine",
                   "Uyarı Sistemi"))

    alerts = []

    if avg_risk > 7:
        alerts.append("🔴 Critical System Risk")
    if trend > 2:
        alerts.append("⚠️ Rapid Risk Increase")
    if df["risk"].max() > 8:
        alerts.append("🔥 Extreme Event Detected")
    if len(df[df["cluster"] == "Military"]) > 3:
        alerts.append("🪖 Military Cluster Build-up")

    if alerts:
        for a in alerts:
            st.write(a)
    else:
        st.write("🟢 No active alerts")

# =========================
# 🔁 REFRESH LOOP
# =========================
time.sleep(60)
st.rerun()