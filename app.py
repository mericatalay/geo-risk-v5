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
st.set_page_config(page_title="Meric Analyst v17", layout="wide")

st.title("🧭 Meric’s Analyst Tool v17")
st.caption("Interactive OSINT Situation Room")

# =========================
# 📡 DATA (RSS)
# =========================
RSS = [
    "https://feeds.bbci.co.uk/news/world/rss.xml",
    "https://www.aljazeera.com/xml/rss/all.xml"
]

def load_feed(url):
    feed = feedparser.parse(url)
    out = []
    for e in feed.entries[:10]:
        out.append({
            "title": e.get("title"),
            "link": e.get("link"),
            "source": url
        })
    return out

events = []
for r in RSS:
    events += load_feed(r)

df = pd.DataFrame(events)

if df.empty:
    st.error("No data")
    st.stop()

# =========================
# 🧠 RISK ENGINE
# =========================
def risk(t):
    t = str(t).lower()
    score = 1
    keywords = {
        "war": 3,
        "attack": 3,
        "oil": 3,
        "gas": 2,
        "shipping": 3,
        "iran": 4,
        "china": 3,
        "russia": 3
    }
    for k, v in keywords.items():
        if k in t:
            score += v
    return min(score, 10)

df["risk"] = df["title"].apply(risk)

# =========================
# 🌍 LOCATION
# =========================
def location(t):
    t = str(t).lower()
    if "iran" in t:
        return [29, 52]
    elif "ukraine" in t:
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
system_score = min(100, avg_risk * 10)

# =========================
# 📊 HEADER
# =========================
c1, c2, c3 = st.columns(3)
c1.metric("System Risk", round(system_score, 1))
c2.metric("Events", len(df))
c3.metric("Status", "🟠 Active Monitoring")

# =========================
# 🗺️ MAP (SMALL)
# =========================
st.subheader("🌍 Situation Map")

df["color_r"] = (df["risk"] * 20).clip(0, 255)
df["color_g"] = 80
df["color_b"] = (255 - df["risk"] * 15).clip(0, 255)

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
    initial_view_state=pdk.ViewState(25, 10, 1.2),
    height=320,
    tooltip={"text": "{title}\nRisk: {risk}"}
))

# =========================
# 📰 CLICKABLE INTELLIGENCE FEED
# =========================
st.subheader("📰 Intelligence Feed (Clickable Sources)")

for _, row in df.sort_values("risk", ascending=False).head(10).iterrows():
    st.markdown(
        f"""
        🔴 **{row['title']}**  
        [Open Source]({row['link']})
        ---
        """
    )

# =========================
# 🌊 CASCADING RISK MODEL (EXPANDABLE)
# =========================
st.subheader("🌊 Cascading Risk Model (Interactive)")

with st.expander("🔋 Energy → Inflation → Food Security"):
    st.write("Energy shocks increase production costs → inflation pressure rises → food prices increase globally.")

with st.expander("🚢 Shipping → Supply Chains"):
    st.write("Disruption in key sea routes increases delivery times and global logistics costs.")

with st.expander("🪖 Conflict → Trade → Economy"):
    st.write("Military escalation impacts trade flows, sanctions and global economic stability.")

# =========================
# 🌍 GLOBAL ECONOMY LAYER
# =========================
st.subheader("🌍 Global Economic Pressure")

oil = df["title"].str.contains("oil|energy", case=False, na=False).mean() * 100
trade = df["title"].str.contains("shipping|trade", case=False, na=False).mean() * 100
conflict = df["title"].str.contains("war|attack", case=False, na=False).mean() * 100

col1, col2, col3 = st.columns(3)

col1.metric("Energy Pressure", f"{oil:.1f}%")
col2.metric("Trade Pressure", f"{trade:.1f}%")
col3.metric("Conflict Pressure", f"{conflict:.1f}%")

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