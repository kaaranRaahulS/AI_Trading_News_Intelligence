TOPIC_WEIGHTS = {
    "fed": 3.0,
    "interest_rates": 3.0,
    "inflation": 2.5,
    "cpi": 2.5,
    "nfp": 2.0,
    "treasury_yields": 2.0,
    "dxy": 2.0,
    "safe_haven": 2.0,
    "recession": 2.0,
    "geopolitical": 1.8,
    "middle_east": 1.8,
    "central_bank_buying": 1.8,
    "etf_flows": 1.5,
    "gold_general": 1.0,
    "mining": 0.8,
    "silver": 0.8,
}

DIRECTIONAL_TAGS = {"bullish", "bearish", "neutral"}

SOURCE_WEIGHTS = {
    "reuters": 1.5,
    "bloomberg": 1.5,
    "financial times": 1.3,
    "wall street journal": 1.3,
    "cnbc": 1.1,
    "the economic times": 1.0,
    "marketwatch": 1.0,
    "investing.com": 1.0,
}

HIGH_INTENSITY_WORDS = {
    "surges": 1.5, "plunges": 1.5, "crashes": 1.5, "soars": 1.5,
    "crisis": 1.4, "war": 1.4, "emergency": 1.4, "collapse": 1.4,
    "shock": 1.3, "unexpected": 1.3, "historic": 1.3, "record": 1.3,
    "jumps": 1.2, "tumbles": 1.2, "spikes": 1.2, "rallies": 1.2,
}


def calculate_impact_score(article) -> tuple:

    tags = getattr(article, "tags", []) or []

    direction = "neutral"
    topic_tags = []
    for tag in tags:
        label = tag["label"] if isinstance(tag, dict) else tag
        if label in DIRECTIONAL_TAGS:
            if label in ("bullish",):
                direction = "bullish"
            elif label in ("bearish",):
                direction = "bearish"
        else:
            topic_tags.append(tag)

    #Topic weight sum
    topic_score = 0.0
    for tag in topic_tags:
        label = tag["label"] if isinstance(tag, dict) else tag
        weight = TOPIC_WEIGHTS.get(label, 0.5)
        if isinstance(tag, dict) and tag.get("in_title"):
            weight *= 1.25
        topic_score += weight

    #Source credibility
    source_lower = getattr(article, "source", "").lower()
    source_mult = 0.8
    for name, w in SOURCE_WEIGHTS.items():
        if name in source_lower:
            source_mult = w
            break

    #Headline intensity
    title_lower = getattr(article, "title", "").lower()
    intensity_mult = max(
        (mult for word, mult in HIGH_INTENSITY_WORDS.items() if word in title_lower),
        default=1.0,
    )

    #Combined total 
    raw_score = topic_score * source_mult * intensity_mult
    impact_score = min(max(round(raw_score / 1.5), 1), 10)

    return impact_score, direction
