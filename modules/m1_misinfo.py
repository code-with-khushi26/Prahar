import feedparser

FEEDS = {
    "BBC": "http://feeds.bbci.co.uk/news/world/rss.xml",
    "AlJazeera": "https://www.aljazeera.com/xml/rss/all.xml",
    "TheHindu": "https://www.thehindu.com/news/national/feeder/default.rss",
}

def fetch_headlines():
    articles = []
    for source, url in FEEDS.items():
        feed = feedparser.parse(url)
        for entry in feed.entries:
            articles.append({
                "title": entry.title,
                "source": source,
                "link": entry.get("link", "")
            })
    return articles