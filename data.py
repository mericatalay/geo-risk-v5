import requests
from datetime import datetime

GDELT_URL = "https://api.gdeltproject.org/api/v2/doc/doc"

def fetch_events(query="Iran OR Hormuz OR oil OR shipping"):
    params = {
        "query": query,
        "mode": "ArtList",
        "format": "json",
        "maxrecords": 50
    }

    r = requests.get(GDELT_URL, params=params, timeout=10)
    data = r.json()

    return data.get("articles", [])