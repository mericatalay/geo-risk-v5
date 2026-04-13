import requests

def fetch_events():
    """
    Robuste GDELT-Abfrage mit stabiler Fallback-Logik
    """

    url = "https://api.gdeltproject.org/api/v2/doc/doc"

    params = {
        "query": "Iran OR Hormuz OR oil OR shipping OR conflict OR war",
        "mode": "ArtList",
        "format": "json",
        "maxrecords": 50,
        "sort": "HybridRel"
    }

    try:
        r = requests.get(url, params=params, timeout=15)

        # 🔍 Status check
        if r.status_code != 200:
            print("HTTP Error:", r.status_code)
            return []

        # 🔍 JSON safe parsing
        try:
            data = r.json()
        except Exception as e:
            print("JSON parse error:", e)
            return []

        # 🔍 flexible field handling
        if "articles" in data:
            return data["articles"]

        if "events" in data:
            return data["events"]

        if "result" in data:
            return data["result"]

        # 🔍 Debug output
        print("Unknown format:", list(data.keys()))
        return []

    except Exception as e:
        print("Request failed:", e)
        return []