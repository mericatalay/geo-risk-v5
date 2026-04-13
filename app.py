import streamlit as st
import time
import pandas as pd
import plotly.express as px

from data import fetch_events
from model import event_score, aggregate_risk, compute_trend, forecast

st.set_page_config(page_title="OSINT Risk v5", layout="wide")

st.title("🌍 Geopolitical Risk Intelligence v5 (OSINT)")

placeholder = st.empty()

# Speicher für Trend
history = []


def build_heatmap(events):
    regions = {"Middle East": 0, "Europe": 0, "Asia": 0, "Global": 0}

    for e in events:
        t = e.get("title", "").lower()

        if "iran" in t or "hormuz" in t:
            regions["Middle East"] += 3
        elif "china" in t:
            regions["Asia"] += 2
        elif "europe" in t:
            regions["Europe"] += 1
        else:
            regions["Global"] += 1

    df = pd.DataFrame({
        "region": list(regions.keys()),
        "risk": list(regions.values())
    })

    return df


while True:

    events = fetch_events()

    risk = aggregate_risk(events)

    history.append(risk)
    if len(history) > 10:
        history.pop(0)

    previous = history[-2] if len(history) > 1 else risk

    trend = compute_trend(risk, previous)
    prediction = forecast(risk, trend)

    heatmap = build_heatmap(events)

    with placeholder.container():

        col1, col2, col3 = st.columns(3)

        col1.metric("Risk Index", f"{risk:.2f}")
        col2.metric("Trend", f"{trend:.2f}")
        col3.metric("Forecast", f"{prediction:.2f}")

        st.progress(int(min(risk, 100)))

        st.markdown("---")

        st.subheader("🔥 Event Stream")

        for e in events[:10]:
            score = event_score(e.get("title", ""))
            st.write(f"{score:.2f} — {e.get('title')}")

        st.markdown("---")

        st.subheader("🌍 Heatmap")

        fig = px.bar(heatmap, x="region", y="risk")
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("---")
        st.write("Raw Events")
        st.json(events[:3])

    time.sleep(15)