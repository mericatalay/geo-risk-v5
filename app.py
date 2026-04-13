import streamlit as st
import pandas as pd
import time
import pydeck as pdk
import feedparser

# =========================
# 🌐 LANGUAGE
# =========================
lang = st.sidebar.selectbox("Language / Sprache / Dil",
                            ["Deutsch", "English", "Türkçe"])

def T(de, en, tr=None):
    return de if lang == "Deutsch" else en if lang == "English" else (tr or en)

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(page_title="Meric Intel v18", layout="wide")

st.title("🧭 Meric’s Intelligence Cockpit v18")
st.caption("Compact OSINT + Geo-Economic Risk System")

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
        "link": e.get("link")
    } for e in feed.entries[:8]]

events = []
for r in RSS:
    events += load(r)

df = pd.DataFrame(events)

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
        "war": 3, "attack": 3, "oil": 3,
        "gas": 2, "shipping": 3,
        "iran": 4, "china": 3, "russia": 3
    }
    for k, v in keys.items():
        if k in t:
            score += v
    return min(score, 10)

df["risk"] = df["title"].apply(risk)

system_score = min(100, df["risk"].mean() * 10)

# =========================
# HEADER KPI (COMPACT)
# =========================
c1, c2, c3 = st.columns([1,1,1])

c1.metric("System Risk", round(system_score, 1))
c2.metric("Events", len(df))
c3.metric("Mode", "ACTIVE MONITORING")

# =========================
# LAYOUT GRID (MAIN)
# =========================
left, mid, right = st.columns([2.2, 2.2, 1.3])

# =========================
# 🗺️ MAP (SMALL + CLEAN)
# =========================
def location(t):
    t = str(t).lower()
    if "iran" in t:
        return [29, 52]
    if "ukraine" in t:
        return [49, 32]
    if "china" in t:
        return [23, 121]
    return [20, 0]

df["lat"] = df["title"].apply(lambda x: location(x)[0])
df["lon"] = df["title"].apply(lambda x: location(x)[1])

df["color_r"] = (df["risk"] * 22).clip(0, 255)
df["color_g"] = 90
df["color_b"] = (255 - df["risk"] * 18).clip(0, 255)

with left:
    st.subheader("🌍 Situation Map")

    layer = pdk.Layer(
        "ScatterplotLayer",
        data=df,
        get_position='[lon, lat]',
        get_radius="risk * 11000",
        get_fill_color='[color_r, color_g, color_b]',
        pickable=True
    )

    st.pydeck_chart(pdk.Deck(
        layers=[layer],
        initial_view_state=pdk.ViewState(25, 10, 1.2),
        height=300,
        tooltip={"text": "{title}\nRisk: {risk}"}
    ))

# =========================
# 🧠 INTELLIGENCE FEED (COMPACT BOX STYLE)
# =========================
with mid:
    st.subheader("📰 Intelligence Feed")

    feed_box = st.container(border=True)

    with feed_box:
        top = df.sort_values("risk", ascending=False).head(10)

        for _, r in top.iterrows():
            risk_icon = "🔴" if r["risk"] > 7 else "🟠" if r["risk"] > 4 else "🟡"

            st.markdown(
                f"""
                <div style="
                    padding:6px;
                    margin-bottom:6px;
                    border-left:3px solid #666;
                    font-size:12px;
                    line-height:1.2;
                ">
                {risk_icon} <a href="{r['link']}" target="_blank">{r['title']}</a>
                </div>
                """,
                unsafe_allow_html=True
            )

# =========================
# 🚨 RIGHT PANEL (CRISIS + ECONOMY)
# =========================
with right:
    st.subheader("🚨 Crisis Hub")

    top3 = df.sort_values("risk", ascending=False).head(3)

    for _, r in top3.iterrows():
        st.markdown(f"🔥 <small>{r['title']}</small>", unsafe_allow_html=True)

    st.markdown("---")

    st.subheader("🌍 Economic Pressure")

    energy = df["title"].str.contains("oil|energy|gas", case=False, na=False).mean() * 100
    trade = df["title"].str.contains("shipping|trade", case=False, na=False).mean() * 100
    conflict = df["title"].str.contains("war|attack|military", case=False, na=False).mean() * 100

    st.metric("Energy", f"{energy:.1f}%")
    st.metric("Trade", f"{trade:.1f}%")
    st.metric("Conflict", f"{conflict:.1f}%")

    st.markdown("---")

    st.subheader("🧠 System Read")

    if system_score < 35:
        st.success("Stable / contained stress")
    elif system_score < 65:
        st.warning("Multi-sector pressure")
    else:
        st.error("Escalation trajectory active")

# =========================
# 🌊 CASCADE (COMPACT FOOTER)
# =========================
st.markdown("---")

with st.expander("🌊 Cascading Risk Model"):
    st.write("Energy shocks → inflation → food prices")
    st.write("Conflict → trade disruption → supply chain delays")
    st.write("Shipping disruption → global price volatility")

# =========================
# 🔁 REFRESH
# =========================
time.sleep(60)
st.rerun()