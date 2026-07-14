"""
scraper.py
Pulls recent defense-related headlines from RSS feeds automatically,
so M1 doesn't need headlines pasted in manually.
"""

import feedparser

FEEDS = [
    "https://www.thehindu.com/news/national/feeder/default.rss",
    "https://www.defenseworld.net/feed",
    "https://timesofindia.indiatimes.com/rssfeeds/1221656.cms",
]

DEFENSE_KEYWORDS = [
    "defence", "defense", "army", "navy", "air force", "DRDO", "military",
    "border", "LAC", "LoC", "missile", "weapon", "IAF", "soldier",
    "China", "Pakistan", "security forces", "terror", "Kashmir"
]


def is_defense_related(title):
    title_lower = title.lower()
    return any(kw.lower() in title_lower for kw in DEFENSE_KEYWORDS)


def fetch_headlines(limit_per_feed=10):
    """Fetch recent headlines from all feeds, filtered to defense-related ones."""
    headlines = []
    for feed_url in FEEDS:
        try:
            parsed = feedparser.parse(feed_url)
            for entry in parsed.entries[:limit_per_feed]:
                title = entry.get("title", "")
                if is_defense_related(title):
                    headlines.append({
                        "title": title,
                        "link": entry.get("link", ""),
                        "published": entry.get("published", ""),
                        "source": feed_url,
                    })
        except Exception as e:
            print(f"Failed to fetch {feed_url}: {e}")
    return headlines