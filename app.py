import streamlit as st
import pandas as pd
import time
import pydeck as pdk

from data import fetch_events
from model import calculate_risk_score

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
st.set_page_config(page_title="Analyst v12", layout="wide")

st.title(T("🧠 Analyst v12 – Intelligence Core",
           "🧠 Analyst v12 – Intelligence Core",
           "🧠 Analist v12 – İstihbarat Çekirdeği"))

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
# 🧠 ENTITY EXTRACTION (LIGHT NLP)
# =========================
def extract_entities(text):
    t = str(text).lower()
    entities = []

    countries = ["iran", "usa", "china", "russia", "ukraine", "israel", "germany"]
    topics = ["oil", "gas", "war", "shipping", "trade", "military", "sanctions"]

    for c in countries:
        if c in t:
            entities.append(c)

    for tp in topics:
        if tp in t:
            entities.append(tp)

    return entities

df["entities"] = df["title"].apply(extract_entities)

# =========================
# 🧩 CLUSTERING (RULE BASED)
# =========================
def cluster(text):
    t = str(text).lower()

    if any(x in t for x in ["oil", "gas", "energy"]):
        return "Energy Cluster"
    elif any(x in t for x in ["ship", "strait", "trade"]):
        return "Trade Cluster"
    elif any(x in t for x in ["war", "attack", "military"]):
        return "Military Cluster"
    elif any(x in t for x in ["sanctions", "diplomacy", "government"]):
        return "Political Cluster"
    else:
        return "General Cluster"

df["cluster"] = df["title"].apply(cluster)

# =========================
# 🚨 SYSTEM STATUS
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
# 📊 KPI
# =========================
c1, c2, c3, c4 = st.columns(4)

c1.metric("Status", status)
c2.metric("Avg Risk", round(avg_risk, 2))
c3.metric("Trend", round(trend, 2))
c4.metric("Clusters", df["cluster"].nunique())

# =========================
# 🧠 CLUSTER VIEW
# =========================
st.subheader(T("🧩 Risiko Cluster",
               "🧩 Risk Clusters",
               "🧩 Risk Grupları"))

cluster_df = df.groupby("cluster")["risk"].mean().sort_values(ascending=False)
st.bar_chart(cluster_df)

# =========================
# 🌍 LOCATION ENGINE
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
# 🎨 COLORS
# =========================
df["color_r"] = (df["risk"] * 25).clip(0, 255)
df["color_g"] = 80
df["color_b"] = (255 - df["risk"] * 20).clip(0, 255)

# =========================
# 🗺️ MAP
# =========================
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

view = pdk.ViewState(
    latitude=25,
    longitude=10,
    zoom=1.4
)

st.subheader(T("🌍 Globale Lagekarte",
               "🌍 Global Situation Map",
               "🌍 Küresel Durum Haritası"))

st.pydeck_chart(pdk.Deck(
    layers=[heat, points],
    initial_view_state=view,
    tooltip={"text": "{title}\nRisk: {risk}\nCluster: {cluster}"}
))

# =========================
# 📰 INTELLIGENCE FEED
# =========================
st.subheader(T("📰 Priorisierte Analyse",
               "📰 Intelligence Feed",
               "📰 İstihbarat Akışı"))

top = df.sort_values("risk", ascending=False).head(7)

for _, row in top.iterrows():
    emoji = "🔴" if row["risk"] > 7 else "🟠" if row["risk"] > 4 else "🟡"
    st.write(f"{emoji} [{row['cluster']}] {row.get('title','No title')}")

# =========================
# 🔁 LOOP
# =========================
time.sleep(60)
st.rerun()