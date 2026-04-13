import streamlit as st
import pandas as pd
import feedparser
import pydeck as pdk
import time

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(page_title="Intel Cockpit v22", layout="wide")

st.markdown("""
<style>
body {
    background-color: #0e1117;
    color: #c9d1d9;
}
.block-container {
    padding-top: 0.8rem;
    padding-bottom: 0rem;
}

.small-card {
    background: #151a22;
    border: 1px solid #2a2f3a;
    padding: 6px;
    margin-bottom: 5px;
    border-radius: 6px;
    font-size: 12px;
    line-height: 1.2;
}

.title {
    font-size: 12px;
    color: #8b949e;
    margin-bottom: 6px;
}
</style>
""", unsafe_allow_html=True)

st.title("🧭 Intel Command Cockpit")
st.caption("OSINT • Geo Risk • Economic Pressure • PONR")

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
        "war": 3,
        "attack": 3,
        "oil": 3,
        "gas": 2,
        "shipping": 3,
        "iran": 4,
        "china": 3,
        "russia": 3
    }
    for k, v in keys.items():
        if k in t:
            score += v
    return min(score, 10)

df["risk"] = df["title"].apply(risk)
system = min(100, df["risk"].mean() * 10)

# =========================
# LAYOUT GRID (REAL INTEL STYLE)
# =========================
left, center, right = st.columns([2.2, 2.6, 1.2])

# =========================
# MAP (LEFT - SMALL + CLEAN)
# =========================
def loc(t):
    t = str(t).lower()
    if "iran" in t: return [29, 52]
    if "ukraine" in t: return [49, 32]
    if "china" in t: return [23, 121]
    return [20, 0]

df["lat"] = df["title"].apply(lambda x: loc(x)[0])
df["lon"] = df["title"].apply(lambda x: loc(x)[1])

df["color"] = (df["risk"] * 22).clip(0, 255)

with left:
    st.markdown("<div class='title'>🌍 GEO HOT ZONES</div>", unsafe_allow_html=True)

    layer = pdk.Layer(
        "ScatterplotLayer",
        data=df,
        get_position='[lon, lat]',
        get_radius="risk * 9000",
        get_fill_color='[color, 80, 180]',
        pickable=True
    )

    st.pydeck_chart(pdk.Deck(
        layers=[layer],
        initial_view_state=pdk.ViewState(25, 10, 1.2),
        height=280
    ))

# =========================
# INTELLIGENCE FEED (CENTER GRID)
# =========================
with center:
    st.markdown("<div class='title'>🧠 INTELLIGENCE GRID</div>", unsafe_allow_html=True)

    top = df.sort_values("risk", ascending=False)

    for _, r in top.iterrows():
        icon = "🔴" if r["risk"] > 7 else "🟠" if r["risk"] > 4 else "🟡"

        st.markdown(f"""
        <div class="small-card">
            {icon} <a href="{r['link']}" target="_blank" style="color:#58a6ff;text-decoration:none;">
            {r['title']}</a>
        </div>
        """, unsafe_allow_html=True)

# =========================
# RIGHT PANEL (CRISIS + ECON + PONR)
# =========================
with right:
    st.markdown("<div class='title'>🚨 CRISIS PANEL</div>", unsafe_allow_html=True)

    top3 = df.sort_values("risk", ascending=False).head(3)

    for _, r in top3.iterrows():
        st.markdown(f"🔥 <span style='font-size:12px'>{r['title']}</span>", unsafe_allow_html=True)

    st.markdown("---")

    st.markdown("<div class='title'>⚠️ PONR</div>", unsafe_allow_html=True)

    ponr = system

    state = (
        "🟢 Stable" if ponr < 40 else
        "🟡 Stress" if ponr < 60 else
        "🟠 Critical" if ponr < 75 else
        "🔴 Near PONR" if ponr < 90 else
        "⚫ PONR"
    )

    st.metric("State", state)
    st.progress(ponr / 100)

    st.markdown("---")

    st.markdown("<div class='title'>🌍 ECON PRESSURE</div>", unsafe_allow_html=True)

    energy = df["title"].str.contains("oil|gas|energy", case=False, na=False).mean() * 100
    trade = df["title"].str.contains("shipping|trade", case=False, na=False).mean() * 100
    conflict = df["title"].str.contains("war|attack", case=False, na=False).mean() * 100

    def label(v):
        if v < 25: return "🟢"
        if v < 50: return "🟡"
        if v < 70: return "🟠"
        if v < 85: return "🔴"
        return "⚫"

    st.write("Energy:", label(energy))
    st.write("Trade:", label(trade))
    st.write("Conflict:", label(conflict))

# =========================
# FOOTER CASCADE
# =========================
st.markdown("---")

with st.expander("🌊 Cascading Risk Model"):
    st.write("Energy → Inflation → Food Prices")
    st.write("Conflict → Trade → Supply Chains")
    st.write("Shipping → Global Price Volatility")

# =========================
# AUTO REFRESH
# =========================
time.sleep(60)
st.rerun()