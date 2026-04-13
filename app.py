import streamlit as st
import pandas as pd
import pydeck as pdk
import feedparser
import time

# =========================
# CONFIG
# =========================
st.set_page_config(page_title="Meric OSINT v20", layout="wide")

st.title("🧭 Meric’s OSINT Command Interface v20")
st.caption("Geopolitical Intelligence • Economic Stress • Cascading Risk • PONR")

# =========================
# DATA SOURCES
# =========================
RSS = [
    "https://feeds.bbci.co.uk/news/world/rss.xml",
    "https://www.aljazeera.com/xml/rss/all.xml"
]

def load(url):
    feed = feedparser.parse(url)
    return [{
        "title": e.get("title"),
        "link": e.get("link"),
        "source": url
    } for e in feed.entries[:8]]

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
# PONR MODEL
# =========================
def ponr(v):
    if v < 40: return ("🟢 Stable", 25)
    if v < 60: return ("🟡 Stress", 50)
    if v < 75: return ("🟠 Critical", 70)
    if v < 90: return ("🔴 Near PONR", 85)
    return ("⚫ PONR", 100)

ponr_label, ponr_index = ponr(system_score)

# =========================
# GRID LAYOUT (COCKPIT STYLE)
# =========================
left, center, right = st.columns([2.4, 2.6, 1.4])

# =========================
# MAP (LEFT - CLEAN HOT ZONES)
# =========================
def loc(t):
    t = str(t).lower()
    if "iran" in t: return [29, 52]
    if "ukraine" in t: return [49, 32]
    if "china" in t: return [23, 121]
    return [20, 0]

df["lat"] = df["title"].apply(lambda x: loc(x)[0])
df["lon"] = df["title"].apply(lambda x: loc(x)[1])

df["color_r"] = (df["risk"] * 22).clip(0, 255)

with left:
    st.subheader("🌍 GEO HOT ZONES")

    layer = pdk.Layer(
        "ScatterplotLayer",
        data=df,
        get_position='[lon, lat]',
        get_radius="risk * 10000",
        get_fill_color='[color_r, 80, 200]',
        pickable=True
    )

    st.pydeck_chart(pdk.Deck(
        layers=[layer],
        initial_view_state=pdk.ViewState(25, 10, 1.2),
        height=320
    ))

# =========================
# INTELLIGENCE GRID (CENTER)
# =========================
with center:
    st.subheader("🧠 Intelligence Grid")

    for _, r in df.sort_values("risk", ascending=False).head(10).iterrows():
        color = "🔴" if r["risk"] > 7 else "🟠" if r["risk"] > 4 else "🟡"

        st.markdown(f"""
        <div style="
            padding:6px;
            margin:4px;
            border-left:3px solid #888;
            font-size:12px;
        ">
        {color} <a href="{r['link']}" target="_blank">{r['title']}</a>
        </div>
        """, unsafe_allow_html=True)

# =========================
# RIGHT PANEL (CRISIS + ECON + PONR)
# =========================
with right:
    st.subheader("🚨 Crisis Panel")

    top = df.sort_values("risk", ascending=False).head(3)
    for _, r in top.iterrows():
        st.write("🔥", r["title"])

    st.markdown("---")

    st.subheader("⚠️ PONR Status")
    st.metric("State", ponr_label)
    st.progress(ponr_index / 100)

    st.markdown("---")

    st.subheader("🌍 Economic Stress")

    energy = df["title"].str.contains("oil|gas|energy", case=False, na=False).mean() * 100
    trade = df["title"].str.contains("shipping|trade", case=False, na=False).mean() * 100
    conflict = df["title"].str.contains("war|attack", case=False, na=False).mean() * 100

    def econ(v):
        if v < 25: return "🟢 Normal"
        if v < 50: return "🟡 Stress"
        if v < 70: return "🟠 Inflation"
        if v < 85: return "🔴 Crisis"
        return "⚫ Shock"

    st.metric("Energy", econ(energy))
    st.metric("Trade", econ(trade))
    st.metric("Conflict", econ(conflict))

# =========================
# CASCADE ENGINE (BOTTOM FULL WIDTH)
# =========================
st.markdown("---")
st.subheader("🌊 Cascading Risk Engine")

with st.expander("Energy → Inflation → Food"):
    st.write("Energy shocks increase production costs → inflation → food insecurity risk increases.")

with st.expander("Trade → Supply Chain → Prices"):
    st.write("Disruptions in shipping routes amplify global price volatility.")

with st.expander("Conflict → Energy → Global Markets"):
    st.write("Geopolitical escalation impacts commodity flows and financial stability.")

# =========================
# AUTO REFRESH
# =========================
time.sleep(60)
st.rerun()