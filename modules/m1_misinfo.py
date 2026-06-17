import feedparser
from transformers import pipeline

FEEDS = {
    "BBC": "http://feeds.bbci.co.uk/news/world/rss.xml",
    "AlJazeera": "https://www.aljazeera.com/xml/rss/all.xml",
    "TheHindu": "https://www.thehindu.com/news/national/feeder/default.rss",
}

# Load models once when module is imported
ner = pipeline("ner", model="dslim/bert-base-NER", aggregation_strategy="simple")
classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

LABELS = [
    "verified defense news from official sources",
    "false or exaggerated military claim",
    "unconfirmed or suspicious defense report"
]

def analyze(text):
    entities = ner(text)
    clf = classifier(text, candidate_labels=LABELS)
    return {
        "text": text,
        "label": clf["labels"][0],
        "score": float(clf["scores"][0]),
        "entities": [
            {"word": e["word"], "type": e["entity_group"]}
            for e in entities
        ]
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