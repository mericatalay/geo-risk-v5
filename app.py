import streamlit as st
import pandas as pd
import feedparser
import pydeck as pdk
import time

# =========================
# CONFIG (BLACK OPS UI)
# =========================
st.set_page_config(page_title="Intel v24", layout="wide")

st.markdown("""
<style>
body {
    background-color: #000000;
    color: #ffffff;
}

.block-container {
    padding-top: 0.5rem;
    background-color: #000000;
    color: #ffffff;
}

.panel {
    background-color: #0b0b0b;
    border: 1px solid #1a1a1a;
    padding: 8px;
    border-radius: 6px;
    margin-bottom: 6px;
    font-size: 12px;
}

.small {
    font-size: 11px;
}

.title {
    font-size: 12px;
    color: #aaaaaa;
    margin-bottom: 6px;
}
</style>
""", unsafe_allow_html=True)

st.title("🧭 Intel Command v24")
st.caption("System Risk Engine • PONR Model • Cascade Intelligence • Early Warning System")

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
    st.error("No data available")
    st.stop()

# =========================
# RISK ENGINE
# =========================
def risk(t):
    t = str(t).lower()
    score = 1
    keys = {
        "war": 3,
        "attack": 3,
        "oil": 3,
        "gas": 2,
        "shipping": 3,
        "iran": 4,
        "china": 3,
        "russia": 3,
        "gaza": 4,
        "israel": 4,
        "inflation": 2
    }
    for k, v in keys.items():
        if k in t:
            score += v
    return min(score, 10)

df["risk"] = df["title"].apply(risk)

system_risk = min(100, df["risk"].mean() * 10)

# =========================
# KRISENINDIKATOREN (CORE SYSTEM MODEL)
# =========================
def indicator_score(df, keywords):
    return df["title"].str.contains("|".join(keywords), case=False, na=False).mean() * 100

energy = indicator_score(df, ["oil", "gas", "energy"])
supply = indicator_score(df, ["shipping", "supply", "port", "trade"])
finance = indicator_score(df, ["inflation", "rate", "market", "bank"])
geo = indicator_score(df, ["war", "attack", "military", "russia", "china", "iran"])
food = indicator_score(df, ["food", "wheat", "agriculture"])
info = indicator_score(df, ["report", "claims", "sources", "confirms"])

# =========================
# CASCADE SCORE (SYSTEM COUPLING)
# =========================
cascade = (
    (energy + supply + geo) / 3
    * (1 + finance / 100)
    * (1 + food / 100)
) / 2

cascade = min(100, cascade)

# =========================
# PONR MODEL (IMPROVED)
# =========================
ponr = (
    system_risk * 0.4 +
    cascade * 0.6
)

distance_to_ponr = max(0, 100 - ponr)

def ponr_state(v):
    if v < 40:
        return "🟢 Stable"
    if v < 60:
        return "🟡 Early Stress"
    if v < 75:
        return "🟠 Systemic Stress"
    if v < 90:
        return "🔴 Near PONR"
    return "⚫ PONR ACTIVE"

state = ponr_state(ponr)

# =========================
# HEADER
# =========================
c1, c2, c3, c4 = st.columns(4)

c1.metric("System Risk", round(system_risk, 1))
c2.metric("Cascade Score", round(cascade, 1))
c3.metric("PONR", round(ponr, 1))
c4.metric("Distance", round(distance_to_ponr, 1))

st.progress(ponr / 100)

st.markdown(f"### ⚠️ Status: {state}")

# =========================
# MAP + CLUSTER
# =========================
def loc(t):
    t = str(t).lower()
    if "iran" in t: return [29, 52]
    if "ukraine" in t: return [49, 32]
    if "china" in t: return [23, 121]
    if "gaza" in t or "israel" in t: return [31, 35]
    return [20, 0]

df["lat"] = df["title"].apply(lambda x: loc(x)[0])
df["lon"] = df["title"].apply(lambda x: loc(x)[1])

df["color"] = (df["risk"] * 22).clip(0, 255)

left, center, right = st.columns([2.3, 2.4, 1.3])

with left:
    st.markdown("### 🌍 Crisis Map")

    layer = pdk.Layer(
        "ScatterplotLayer",
        data=df,
        get_position='[lon, lat]',
        get_radius="risk * 8000",
        get_fill_color='[color, 60, 200]',
        pickable=True
    )

    st.pydeck_chart(pdk.Deck(
        layers=[layer],
        initial_view_state=pdk.ViewState(
            latitude=df["lat"].mean(),
            longitude=df["lon"].mean(),
            zoom=1.5
        ),
        height=320
    ))

# =========================
# INTELLIGENCE FEED
# =========================
with center:
    st.markdown("### 🧠 Intelligence Feed")

    for _, r in df.sort_values("risk", ascending=False).head(12).iterrows():
        icon = "🔴" if r["risk"] > 7 else "🟠" if r["risk"] > 4 else "🟡"

        st.markdown(f"""
        <div class="panel">
        {icon} <a href="{r['link']}" target="_blank" style="color:white;text-decoration:none;">
        {r['title']}</a>
        </div>
        """, unsafe_allow_html=True)

# =========================
# RIGHT PANEL (FULL MODEL)
# =========================
with right:
    st.markdown("### ⚠️ Crisis Indicators")

    st.write("🛢 Energy:", round(energy, 1), "%")
    st.write("🚢 Supply:", round(supply, 1), "%")
    st.write("💰 Finance:", round(finance, 1), "%")
    st.write("🪖 Geo:", round(geo, 1), "%")
    st.write("🌾 Food:", round(food, 1), "%")
    st.write("📡 Info:", round(info, 1), "%")

    st.markdown("---")

    st.markdown("### 🌊 Cascade Logic")
    st.write("System coupling of energy + supply + geopolitics + finance")

    st.metric("Cascade Score", round(cascade, 1))

    st.markdown("---")

    st.markdown("### ⚠️ PONR Engine")
    st.metric("PONR Level", round(ponr, 1))
    st.metric("Distance", round(distance_to_ponr, 1))
    st.write(state)

# =========================
# CASCADE DETAILS
# =========================
st.markdown("---")

with st.expander("🌊 Early Warning Model Explanation"):
    st.write("""
    - Energy + Supply Chain disruption increases systemic fragility
    - Geopolitical escalation amplifies financial stress
    - Food system reacts with delay (lagging indicator)
    - Cascade Score measures interconnection strength
    - PONR = nonlinear threshold where feedback loops dominate
    """)

# =========================
# AUTO REFRESH
# =========================
time.sleep(60)
st.rerun()