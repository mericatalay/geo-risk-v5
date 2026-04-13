import streamlit as st
import pandas as pd
import plotly.express as px
import time

from data import fetch_events
from model import calculate_risk_score

st.set_page_config(page_title="Geo Risk Dashboard", layout="wide")

st.title("🌍 Geopolitisches Frühwarn-Dashboard")

# 🔄 Auto Refresh
st.caption("Auto-Update alle 60 Sekunden")
time.sleep(1)

# 📡 Daten laden
events = fetch_events()

if not events:
    st.warning("⚠️ Keine aktuellen Daten verfügbar (API Problem oder leer)")
    st.stop()

# 📊 DataFrame bauen
df = pd.DataFrame(events)

# 🧠 Dummy-Scores berechnen (anpassbar)
df["risk_score"] = df.apply(lambda x: calculate_risk_score(x), axis=1)

# 📈 KPI
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Events", len(df))

with col2:
    st.metric("Ø Risiko", round(df["risk_score"].mean(), 2))

with col3:
    st.metric("Max Risiko", round(df["risk_score"].max(), 2))

# 📊 Chart 1 (ZEIT / INDEX)
df["index"] = range(len(df))

fig1 = px.line(df, x="index", y="risk_score", title="Risikoverlauf")

st.plotly_chart(fig1, use_container_width=True, key="chart_main")  # ✅ FIX

# 📊 Chart 2 (Verteilung)
fig2 = px.histogram(df, x="risk_score", nbins=20, title="Risikoverteilung")

st.plotly_chart(fig2, use_container_width=True, key="chart_hist")  # ✅ FIX

# 📰 News anzeigen
st.subheader("📰 Letzte Ereignisse")

for i, row in df.head(10).iterrows():
    st.write(f"**{row.get('title', 'Kein Titel')}**")
    st.write(f"Risiko: {row['risk_score']}")
    st.write("---")

# 🔁 Auto Refresh Trigger
st.caption("Letztes Update: Jetzt")