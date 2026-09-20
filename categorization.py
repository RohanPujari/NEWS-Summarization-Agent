def categorize_article(title: str, summary: str) -> str:
    """Categorize an article using weighted keyword matching."""

    text = f"{title} {summary}".lower()

    categories = {
        "sports": [
            "nfl", "nba", "mlb", "nhl", "ncaa",
            "football", "basketball", "baseball", "hockey",
            "soccer", "tennis", "golf",
            "touchdown", "quarterback", "pitcher", "goalkeeper",
            "coach", "athlete", "sports", "sport",
            "playoff", "championship", "tournament",
            "league", "match", "game",
            "player", "team", "season"
        ],

        "technology": [
            "artificial intelligence", "machine learning",
            "generative ai", "large language model", "llm",
            "chatgpt", "openai", "google ai",
            "software", "hardware", "semiconductor",
            "chip", "cybersecurity", "cyber attack",
            "data breach", "cloud computing",
            "smartphone", "iphone", "android",
            "microsoft", "google", "amazon",
            "apple", "meta", "nvidia",
            "spacex", "nasa", "rocket", "satellite",
            "robot", "robotics", "algorithm",
            "technology", "tech", "internet",
            "blockchain", "cryptocurrency"
        ],

        "finance": [
            "stock market", "stock", "stocks",
            "nasdaq", "dow jones", "s&p 500",
            "wall street", "share price",
            "investor", "investors", "investment",
            "trading", "trader",
            "bank", "banking",
            "interest rate", "federal reserve", "fed",
            "inflation", "recession",
            "earnings", "revenue", "profit",
            "ipo", "bond", "treasury",
            "financial", "finance",
            "bitcoin", "ethereum", "crypto"
        ],

        "health": [
            "health", "healthcare", "medical",
            "doctor", "nurse", "hospital",
            "patient", "disease", "cancer",
            "virus", "vaccine", "pandemic",
            "medication", "medicine", "treatment",
            "clinical trial", "diagnosis",
            "mental health", "fitness",
            "exercise", "diet", "nutrition",
            "wellness", "public health"
        ],

        "politics": [
            "president", "presidential",
            "trump", "biden", "harris",
            "republican", "democrat",
            "election", "elections",
            "vote", "voting", "ballot",
            "congress", "senate", "senator",
            "house of representatives",
            "government", "governor", "mayor",
            "parliament",
            "political", "politics",
            "campaign", "rally",
            "immigration", "immigrant",
            "border policy",
            "legislation", "legislative",
            "bill", "law", "policy",
            "executive order", "supreme court",
            "impeachment"
        ],

        "entertainment": [
            "movie", "film", "actor", "actress",
            "celebrity", "music", "singer",
            "band", "album", "concert",
            "hollywood", "netflix",
            "oscars", "grammy", "emmy",
            "award", "awards",
            "director", "producer",
            "broadway", "theater",
            "television", "tv show",
            "streaming"
        ]
    }

    # Count keyword matches.
    scores = {}

    for category, keywords in categories.items():
        score = 0

        for keyword in keywords:
            if keyword in text:
                # Multi-word / highly specific terms are stronger signals.
                if " " in keyword:
                    score += 3
                else:
                    score += 1

        scores[category] = score

    # Strong signals that should override weaker cross-category matches.
    strong_signals = {
        "sports": [
            "nfl", "nba", "mlb", "nhl", "football",
            "basketball", "baseball", "hockey",
            "soccer", "tennis", "touchdown",
            "quarterback", "playoff"
        ],
        "politics": [
            "election", "voting", "congress",
            "senate", "president", "immigration",
            "republican", "democrat", "legislation",
            "executive order", "supreme court"
        ],
        "technology": [
            "artificial intelligence", "machine learning",
            "generative ai", "chatgpt", "openai",
            "cybersecurity", "cyber attack",
            "spacex", "nasa", "rocket", "satellite"
        ],
        "finance": [
            "stock market", "nasdaq", "dow jones",
            "wall street", "federal reserve",
            "interest rate", "inflation",
            "earnings", "ipo"
        ],
        "health": [
            "clinical trial", "mental health",
            "public health", "vaccine",
            "cancer", "hospital"
        ],
        "entertainment": [
            "oscars", "grammy", "emmy",
            "hollywood", "netflix",
            "concert", "movie", "film"
        ]
    }

    for category, keywords in strong_signals.items():
        if any(keyword in text for keyword in keywords):
            return category

    best_category = max(scores, key=scores.get)

    if scores[best_category] == 0:
        return "general"

    return best_category
