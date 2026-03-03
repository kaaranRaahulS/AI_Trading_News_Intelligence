import re
from typing import List, Dict

RULES = {
    "instrument": {
        "xauusd": [
            r"\bxau\/?usd\b",
            r"\bxauusd\b",
            r"\bspot\s*gold\b",
            r"\bgold\s*futures?\b",
            r"\bcomex\s*gold\b",
        ],
        "gold_general": [
            r"\bgold\s*price[s]?\b",
        ]
    },

    "macro_drivers": {
        "inflation": [
            r"\binflation\b",
            r"\bcpi\b",
            r"\bconsumer\s*price\b",
            r"\bppi\b",
            r"\bproducer\s*price\b",
        ],
        "fed_policy": [
            r"\bfomc\b",
            r"\bfederal\s*reserve\b",
            r"\bpowell\b",
        ],
        "rates": [
            r"\binterest\s*rates?\b",
            r"\brate\s*hike\b",
            r"\brate\s*cut\b",
        ],
        "dxy": [
            r"\bdxy\b",
            r"\bdollar\s*index\b",
        ],
        "yields": [
            r"\breal\s*yields?\b",
            r"\b10[-\s]?year\s*(yield|treasury)\b",
            r"\b2[-\s]?year\s*(yield|treasury)\b",
        ],
        "employment": [
            r"\bnon-?farm\s*payroll[s]?\b",
            r"\bnfp\b",
            r"\bunemployment\b",
            r"\bjobs\s*report\b",
        ],
        "recession": [
            r"\brecession\b",
            r"\beconomic\s*downturn\b",
            r"\bcontraction\b",
        ],
        "etf_flows": [
            r"\bspdr\s*gold\s*trust\b",
            r"\bgld\s*etf\b",
            r"\bgold\s*etf\s*holdings?\b",
        ]
    },

    "geopolitics": {
        "middle_east": [
            r"\bisrael\b",
            r"\biran\b",
            r"\bgaza\b",
            r"\bmiddle\s*east\b",
        ],
        "russia_ukraine": [
            r"\bukraine\b",
            r"\brussia\b",
        ],
        "sanctions": [
            r"\bsanction[s]?\b",
            r"\bembargo\b",
        ],
    },

    "sentiment": {
        "bullish": [
            r"\bbullish\b",
            r"\brally\b",
            r"\bsurge[ds]?\b",
            r"\brecord\s*high\b",
            r"\ball[-\s]?time\s*high\b",
        ],
        "bearish": [
            r"\bbearish\b",
            r"\bplunge[ds]?\b",
            r"\bcrash\b",
            r"\bslump[sed]?\b",
            r"\bsell[\s-]?off\b",
        ],
        "safe_haven": [
            r"\bsafe[\s-]?haven\b",
            r"\bflight\s*to\s*safety\b",
            r"\brisk[\s-]?off\b",
        ],
        "risk_on": [
            r"\brisk[\s-]?on\b",
            r"\brisk\s*appetite\b",
        ],
        "technical": [
            r"\bsupport\b",
            r"\bresistance\b",
            r"\bbreakout\b",
            r"\btechnical\s*analysis\b",
        ]
    }
}

COMPILED_RULES = []

for category, subgroups in RULES.items():
    for label, patterns in subgroups.items():
        for pattern in patterns:
            COMPILED_RULES.append({
                "regex": re.compile(pattern, re.IGNORECASE),
                "label": label,
                "category": category
            })


def tag_article(title: str, content: str) -> List[Dict]:

    tags = []
    seen = set()

    for rule in COMPILED_RULES:
        label = rule["label"]
        category = rule["category"]
        regex = rule["regex"]

        if regex.search(title) or regex.search(content):
            key = (category, label)
            if key not in seen:
                seen.add(key)
                tags.append({
                    "category": category,
                    "label": label,
                    "in_title": bool(regex.search(title))
                })

    return tags

WEIGHTS = {
    "instrument": 5,
    "macro_drivers": 3,
    "geopolitics": 2,
    "sentiment": 1,
}

def score_tags(tags: List[Dict]) -> int:
    score = 0
    for t in tags:
        score += WEIGHTS.get(t["category"], 0)
    return score

def display_tags(title: str, tags: List[Dict]) -> None:
    print(f"\n  {title[:90]}")
    if not tags:
        print("    (no tags)")
        return

