def calculate_risk_score(row):
    """
    Berechnet einen einfachen, stabilen Risk Score
    basierend auf dem News-Text.
    """

    score = 0

    # Titel sicher extrahieren
    title = str(row.get("title", "")).lower()

    # 🔥 Hochrisiko-Trigger
    high_risk_keywords = [
        "war",
        "attack",
        "missile",
        "explosion",
        "blockade",
        "strike"
    ]

    # ⚠️ geopolitische Trigger
    medium_risk_keywords = [
        "iran",
        "hormuz",
        "strait",
        "oil",
        "sanctions",
        "military",
        "conflict",
        "shipping"
    ]

    # 🔴 High Risk Gewichtung
    for word in high_risk_keywords:
        if word in title:
            score += 4

    # 🟠 Medium Risk Gewichtung
    for word in medium_risk_keywords:
        if word in title:
            score += 2

    # 📊 Normalisierung (optional stabiler Output)
    if score > 10:
        score = 10

    return score


def normalize_risk(scores):
    """
    Optional: Durchschnittsrisiko aus Liste von Scores
    """
    if not scores:
        return 0

    return sum(scores) / len(scores)