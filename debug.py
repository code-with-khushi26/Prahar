from scraper import FEEDS
import feedparser

for url in FEEDS:
    print(f"\n--- {url} ---")
    parsed = feedparser.parse(url)
    print(f"Entries found: {len(parsed.entries)}")
    if parsed.bozo:
        print(f"Feed error: {parsed.bozo_exception}")
    for entry in parsed.entries[:3]:
        print(" -", entry.get("title", "NO TITLE"))