import feedparser
from transformers import pipeline, DistilBertForSequenceClassification, DistilBertTokenizer
import torch

# Load fine-tuned model
model_path = "models/m1_misinfo"
tokenizer = DistilBertTokenizer.from_pretrained(model_path)
ft_model = DistilBertForSequenceClassification.from_pretrained(model_path)
ft_pipeline = pipeline("text-classification", model=ft_model, tokenizer=tokenizer)

# Zero-shot classifier (base model)
zero_shot = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

LABELS = [
    "verified defense news from official sources",
    "false or exaggerated military claim",
    "unconfirmed or suspicious defense report"
]

FEEDS = {
    "BBC": "http://feeds.bbci.co.uk/news/world/rss.xml",
    "AlJazeera": "https://www.aljazeera.com/xml/rss/all.xml",
    "TheHindu": "https://www.thehindu.com/news/national/feeder/default.rss",
}

def analyze(text):
    # Fine-tuned model result
    ft_result = ft_pipeline(text)[0]
    ft_label = "REAL" if ft_result["label"] == "LABEL_1" else "FAKE"
    
    # Zero-shot result
    zs_result = zero_shot(text, candidate_labels=LABELS)
    zs_label = zs_result["labels"][0]

    return {
        "text": text,
        "finetuned": {
            "label": ft_label,
            "score": round(ft_result["score"], 3)
        },
        "zeroshot": {
            "label": zs_label,
            "score": round(zs_result["scores"][0], 3)
        }
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