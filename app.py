import streamlit as st
import pandas as pd
import plotly.express as px
import time

from data import fetch_events
from model import calculate_risk_score

st.set_page_config(page_title="Cognitive Risk Dashboard", layout="wide")

# =========================
# 🧠 UI HEADER (HUMAN MODE)
# =========================
st.title("🌍 Geopolitical Situation Overview")

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
# 🚨 SIMPLE GLOBAL STATUS
# =========================
avg_risk = df["risk"].mean()

if avg_risk > 7:
    status = "🔴 HIGH RISK"
elif avg_risk > 4:
    status = "🟠 ELEVATED"
elif avg_risk > 2:
    status = "🟡 WATCH"
else:
    status = "🟢 STABLE"

st.markdown(f"## Status: {status}")

st.progress(min(int(avg_risk * 10), 100))

# =========================
# 🌍 REGION VIEW (HUMAN MAP SUBSTITUTE)
# =========================
st.subheader("🌍 Regional Pressure Overview")

regions = {
    "Middle East": 0,
    "Europe": 0,
    "Asia": 0,
    "Global": 0
}

for t in df["title"]:
    t = str(t).lower()

    if "iran" in t or "hormuz" in t:
        regions["Middle East"] += 1
    elif "china" in t or "taiwan" in t:
        regions["Asia"] += 1
    elif "europe" in t:
        regions["Europe"] += 1
    else:
        regions["Global"] += 1

region_df = pd.DataFrame({
    "region": list(regions.keys()),
    "pressure": list(regions.values())
})

fig_map = px.bar(region_df, x="region", y="pressure")
st.plotly_chart(fig_map, use_container_width=True, key="map")

# =========================
# 📈 TREND (SIMPLIFIED)
# =========================
st.subheader("📈 Risk Trend (Simple View)")

df["index"] = range(len(df))

fig_trend = px.line(df, x="index", y="risk")
st.plotly_chart(fig_trend, use_container_width=True, key="trend")

# =========================
# 📰 TOP EVENTS (FILTERED HUMAN VIEW)
# =========================
st.subheader("📰 Key Developments")

top = df.sort_values("risk", ascending=False).head(5)

for _, row in top.iterrows():
    emoji = "🔴" if row["risk"] > 7 else "🟠" if row["risk"] > 4 else "🟡"
    st.write(f"{emoji} {row.get('title','No title')}")

# =========================
# 🔁 AUTO REFRESH
# =========================
time.sleep(60)
st.rerun()