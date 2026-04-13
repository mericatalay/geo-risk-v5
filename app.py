import streamlit as st
import pandas as pd
import feedparser
import pydeck as pdk
import time

# =========================
# CONFIG
# =========================
st.set_page_config(page_title="Intel v27", layout="wide")

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

st.title("🧭 Intel Command v27")
st.caption("Scenario Intelligence • Trigger Engine • System Forecast AI")

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
        "ukraine": 4,
        "gaza": 4,
        "israel": 4,
        "inflation": 2,
        "sanction": 3
    }
    for k, v in keys.items():
        if k in t:
            score += v
    return min(score, 10)

df["risk"] = df["title"].apply(risk)

system_risk = df["risk"].mean()

# =========================
# AXES (SYSTEM STATE)
# =========================
def axis(keywords):
    return df["title"].str.contains("|".join(keywords), case=False, na=False).mean() * 10

energy = axis(["oil", "gas", "energy"])
geo = axis(["war", "attack", "military", "russia", "china", "iran"])
finance = axis(["inflation", "bank", "market", "rate"])
supply = axis(["shipping", "trade", "port", "supply"])
ukraine = axis(["ukraine", "kyiv", "front", "russia"])
food = axis(["food", "wheat", "agriculture"])

cascade = (energy + geo + finance + supply + ukraine) / 5
ponr = (system_risk + cascade) / 2

# =========================
# TRIGGER ENGINE (NEW CORE)
# =========================
triggers = {
    "Energy Shock": energy > 6,
    "Geopolitical Escalation": geo > 6,
    "Financial Stress": finance > 6,
    "Ukraine Intensification": ukraine > 6,
    "Supply Chain Strain": supply > 6
}

trigger_score = sum(triggers.values())

# =========================
# SCENARIO ENGINE (PROBABILISTIC MODEL)
# =========================

# base weights from system state
worst = min(100, (ponr * 8) + (trigger_score * 8))
stable = max(0, 100 - worst - 20)
deescalation = max(0, 100 - worst - 40)

total = worst + stable + deescalation

worst_p = round(worst / total * 100, 1)
stable_p = round(stable / total * 100, 1)
deesc_p = round(deescalation / total * 100, 1)

# scenario selection
scenario = max([
    ("🔴 Worst Case", worst_p),
    ("🟡 Status Quo", stable_p),
    ("🟢 De-escalation", deesc_p)
], key=lambda x: x[1])[0]

# =========================
# FORECAST
# =========================
trend = cascade - system_risk

if trend > 0.8:
    forecast = "🔴 Escalation Dominates"
elif trend > 0.2:
    forecast = "🟠 Rising Stress"
elif trend > -0.2:
    forecast = "🟡 Stable"
else:
    forecast = "🟢 Cooling"

# =========================
# HEADER
# =========================
st.markdown("## 🧠 AI Scenario Forecast")

st.markdown(f"### {forecast}")
st.markdown(f"### Active Scenario: **{scenario}**")

c1, c2, c3 = st.columns(3)
c1.metric("Worst Case", f"{worst_p}%")
c2.metric("Status Quo", f"{stable_p}%")
c3.metric("De-escalation", f"{deesc_p}%")

st.progress(ponr / 10)

st.markdown(f"### ⚠️ PONR Level: {ponr:.2f}/10")

# =========================
# TRIGGER PANEL
# =========================
st.markdown("## ⚡ Trigger Detection")

for k, v in triggers.items():
    st.write(("🔴" if v else "🟢"), k)

# =========================
# SYSTEM AXES
# =========================
st.markdown("## 📊 System Axes (0–10)")

def bar(n, v):
    st.write(f"{n}: {v:.2f}/10")
    st.progress(v / 10)

bar("🛢 Energy", energy)
bar("🪖 Geopolitical", geo)
bar("💰 Finance", finance)
bar("🚢 Supply Chain", supply)
bar("🇺🇦 Ukraine", ukraine)

# =========================
# FEED
# =========================
st.markdown("## 🧠 Intelligence Feed")

for _, r in df.sort_values("risk", ascending=False).head(10).iterrows():
    icon = "🔴" if r["risk"] > 7 else "🟠" if r["risk"] > 4 else "🟡"

    st.markdown(f"""
    <div class="panel">
    {icon} <a href="{r['link']}" target="_blank" style="color:white;text-decoration:none;">
    {r['title']}</a>
    </div>
    """, unsafe_allow_html=True)

# =========================
# EXPLANATION
# =========================
st.markdown("---")

with st.expander("🧠 Scenario Model Logic"):
    st.write("""
    - Worst Case increases with PONR + trigger density
    - Status Quo dominates in medium-stress equilibrium
    - De-escalation emerges when system coupling drops
    - Triggers act as nonlinear amplification points
    - System is not linear: multiple small triggers = large shift
    """)

# =========================
# REFRESH
# =========================
time.sleep(60)
st.rerun()