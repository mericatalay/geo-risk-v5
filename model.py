import re
import time

RISK_WORDS = {
    "war": 0.9,
    "attack": 0.8,
    "missile": 0.9,
    "blockade": 0.85,
    "oil": 0.5,
    "sanctions": 0.7,
    "explosion": 0.85,
    "shipping": 0.4,
    "strait": 0.8
}

def event_score(text):
    text = text.lower()
    score = 0

    for k, v in RISK_WORDS.items():
        if re.search(k, text):
            score += v

    return min(score, 1.0)


def aggregate_risk(events):
    if not events:
        return 0

    scores = [event_score(e.get("title", "")) for e in events]
    return sum(scores) / len(scores) * 100


# einfache Trendlogik (letzte vs vorherige Events)
def compute_trend(current, previous):
    return current - previous


def forecast(risk, trend):
    # bewusst simpel & transparent
    return min(100, risk * 0.7 + trend * 30)