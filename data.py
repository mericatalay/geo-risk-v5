import requests
import feedparser

# ----------------------------
# 1. GDELT (optional)
# ----------------------------
def fetch_gdelt():
    url = "https://api.gdeltproject.org/api/v2/doc/doc"

    params = {
        "query": "Iran OR Hormuz OR oil OR shipping OR conflict",
        "mode": "ArtList",
        "format": "json",
        "maxrecords": 30
    }

    try:
        r = requests.get(url, params=params, timeout=10)

        data = r.json()

        if "articles" in data:
            return [{"title": a.get("title", "")} for a in data["articles"]]

    except:
        pass

    return []


# ----------------------------
# 2. RSS BACKUP (STABIL!)
# ----------------------------
def fetch_rss():
    feeds = [
        "http://feeds.bbci.co.uk/news/world/rss.xml",
        "https://www.aljazeera.com/xml/rss/all.xml"
    ]

    results = []

    for url in feeds:
        try:
            feed = feedparser.parse(url)

            for entry in feed.entries[:10]:
                results.append({
                    "title": entry.get("title", "")
                })

        except:
            continue

    return results


# ----------------------------
# MAIN FUNCTION (HYBRID)
# ----------------------------
def fetch_events():
    gdelt = fetch_gdelt()
    rss = fetch_rss()

    combined = gdelt + rss

    # fallback guarantee
    if not combined:
        return [{"title": "No data available"}]

    return combined