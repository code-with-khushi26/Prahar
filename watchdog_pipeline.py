"""
watchdog_pipeline.py
Combines the RSS scraper, your existing classifier (m1_misinfo.analyze),
and the LLM-based fact checker (factcheck.fact_check) into one pipeline —
this is what turns manual "paste a headline" into automated "watch the news."
"""

from scraper import fetch_headlines
from modules.m1_misinfo import analyze
from modules.factcheck import fact_check


def run_watchdog_cycle(limit_per_feed=10):
    """
    Fetches fresh defense headlines, runs each through the existing
    classifier AND the LLM cross-check, and returns a combined verdict
    per headline.
    """
    headlines = fetch_headlines(limit_per_feed=limit_per_feed)
    results = []

    for h in headlines:
        title = h["title"]

        classifier_result = analyze(title)
        crosscheck_result = fact_check(title)

        results.append({
            "headline": title,
            "source_link": h["link"],
            "published": h["published"],
            "classifier": classifier_result,
            "llm_crosscheck": crosscheck_result,
            # simple combined verdict: flag if either says FAKE/FALSE
            "final_flag": (
                classifier_result.get("finetuned", {}).get("label") == "FAKE"
                or crosscheck_result.get("verdict") == "FALSE"
            ),
        })

    return results