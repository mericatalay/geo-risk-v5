import requests
from datetime import datetime

GDELT_URL = "https://api.gdeltproject.org/api/v2/doc/doc"

import requests

def fetch_events():
    url = "https://api.gdeltproject.org/api/v2/events/search"

    params = {
        "query": "Iran Strait Hormuz shipping conflict",
        "mode": "ArtList",
        "format": "json",
        "maxrecords": 50
    }

    try:
        r = requests.get(url, params=params, timeout=10)

        # 🔍 DEBUG: Status prüfen
        if r.status_code != 200:
            print("API Fehler:", r.status_code)
            return []

        # 🔍 Versuche JSON zu lesen
        try:
            data = r.json()
        except Exception:
            print("Keine gültige JSON-Antwort:")
            print(r.text[:500])  # zeigt ersten Teil der Antwort
            return []

        # 🔍 Prüfen ob Inhalt existiert
        if "articles" not in data:
            print("Keine Artikel im Response")
            return []

        return data["articles"]

    except requests.exceptions.RequestException as e:
        print("Request fehlgeschlagen:", e)
        return []