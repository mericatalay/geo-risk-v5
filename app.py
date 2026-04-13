import streamlit as st
import pandas as pd
import feedparser
import matplotlib.pyplot as plt
import time

# =========================
# CONFIG
# =========================
st.set_page_config(page_title="Intel v28", layout="wide")

st.markdown("""
<style>
body { background-color: #000; color: #fff; }
.block-container { padding-top: 0.5rem; }

.panel {
    background-color: #0b0b0b;
    border: 1px solid #1a1a1a;
    padding: 8px;
    border-radius: 6px;
    margin-bottom: 6px;
    font-size: 12px;
}
</style>
""", unsafe_allow_html=True)

st.title("🧭 Intel Command v28")
st.caption("Visual Intelligence System • Scenario AI • Trigger Engine • PONR Bars")

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
    } for e in feed.entries[:15]]

df = pd.DataFrame(sum([load(r) for r in RSS], []))

if df.empty:
    st.error("No data")
    st.stop()

# =========================
# RISK ENGINE
# =========================
def score(text, keywords):
    return text.str.contains("|".join(keywords), case=False, na=False).mean() * 10

energy = score(df["title"], ["oil", "gas", "energy"])
geo = score(df["title"], ["war", "attack", "military", "russia", "china", "iran"])
finance = score(df["title"], ["inflation", "bank", "market", "rate"])
supply = score(df["title"], ["shipping", "trade", "supply", "port"])
ukraine = score(df["title"], ["ukraine", "kyiv", "front", "russia"])

system_risk = df["title"].str.contains("war|attack|oil|gas", case=False, na=False).mean() * 10

cascade = (energy + geo + finance + supply + ukraine) / 5
ponr = (system_risk + cascade) / 2

# =========================
# TRIGGERS
# =========================
triggers = {
    "Energy Shock": energy,
    "Geopolitical Stress": geo,
    "Financial Stress": finance,
    "Supply Chain Stress": supply,
    "Ukraine Pressure": ukraine
}

# =========================
# SCENARIOS
# =========================
worst = ponr * 9
stable = max(0, 100 - worst - 10)
deesc = max(0, 100 - worst - 25)

total = worst + stable + deesc

scenarios = {
    "Worst Case": worst / total * 100,
    "Status Quo": stable / total * 100,
    "De-escalation": deesc / total * 100
}

active_scenario = max(scenarios, key=scenarios.get)

# =========================
# HEADER
# =========================
st.markdown("## 🧠 Visual Forecast")

st.markdown(f"### 🔮 Active Scenario: **{active_scenario}**")

c1, c2, c3 = st.columns(3)
c1.metric("System Risk", round(system_risk, 2))
c2.metric("Cascade", round(cascade, 2))
c3.metric("PONR", round(ponr, 2))

st.progress(ponr / 10)

# =========================
# 📊 BAR CHART FUNCTION
# =========================
def bar_chart(labels, values, title):
    fig, ax = plt.subplots()
    ax.barh(labels, values)
    ax.set_xlim(0, 10)
    ax.set_title(title)
    st.pyplot(fig)

# =========================
# VISUAL BLOCKS
# =========================
st.markdown("## 📊 System Axes (0–10)")

bar_chart(
    ["Energy", "Geo", "Finance", "Supply", "Ukraine"],
    [energy, geo, finance, supply, ukraine],
    "System Stress Levels"
)

st.markdown("## ⚠️ PONR Visualization")

bar_chart(
    ["PONR"],
    [ponr],
    "Point of No Return Risk"
)

st.markdown("## 🔮 Scenario Distribution")

bar_chart(
    list(scenarios.keys()),
    list(scenarios.values()),
    "Scenario Probabilities (%)"
)

# =========================
# TRIGGERS
# =========================
st.markdown("## ⚡ Trigger Engine")

for k, v in triggers.items():
    color = "🔴" if v > 6 else "🟠" if v > 3 else "🟢"
    st.write(color, f"{k}: {round(v,2)}/10")

# =========================
# FEED
# =========================
st.markdown("## 🧠 Intelligence Feed")

for _, r in df.head(10).iterrows():
    st.markdown(f"""
    <div class="panel">
    🔹 <a href="{r['link']}" target="_blank" style="color:white;text-decoration:none;">
    {r['title']}</a>
    </div>
    """, unsafe_allow_html=True)

# =========================
# EXPLANATION
# =========================
st.markdown("---")

with st.expander("🧠 Model Explanation"):
    st.write("""
    - Bars represent system stress intensity (0–10)
    - PONR is combined systemic instability index
    - Scenarios are probability-weighted system outcomes
    - Triggers show local stress amplification points
    - System is nonlinear: multiple medium bars = escalation risk
    """)

# =========================
# REFRESH
# =========================
time.sleep(60)
st.rerun()