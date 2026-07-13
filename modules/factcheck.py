"""
factcheck.py
Cross-checks a news headline/claim against real web search results using
DuckDuckGo (free, no API key) + Groq (free, fast LLM) to give a grounded
verdict instead of the model just guessing from training data.
"""

import os
from dotenv import load_dotenv
load_dotenv()

from ddgs import DDGS
from groq import Groq

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
MODEL_NAME = "llama-3.3-70b-versatile"


def search_web(query, max_results=5):
    """Search DuckDuckGo for the claim and return top result snippets."""
    results = []
    with DDGS() as ddgs:
        for r in ddgs.text(query, max_results=max_results):
            results.append({
                "title": r.get("title", ""),
                "snippet": r.get("body", ""),
                "url": r.get("href", ""),
            })
    return results


def fact_check(claim):
    """
    Searches the web for the claim, then asks the LLM to verify it
    strictly based on the retrieved snippets (not its own memory).
    Returns a verdict: TRUE / FALSE / UNVERIFIED, with explanation and sources.
    """
    search_results = search_web(claim)

    if not search_results:
        return {
            "claim": claim,
            "verdict": "UNVERIFIED",
            "explanation": "No web search results found to verify this claim.",
            "sources": [],
        }

    context = "\n\n".join(
        f"Source {i+1}: {r['title']}\n{r['snippet']}\nURL: {r['url']}"
        for i, r in enumerate(search_results)
    )

    prompt = f"""You are a fact-checking assistant. Verify the following claim
using ONLY the search results provided below. Do not use any prior knowledge
you may have — base your answer strictly on these sources, since they are
more current than your training data.

CLAIM: "{claim}"

SEARCH RESULTS:
{context}

Respond in this exact format:
VERDICT: [TRUE / FALSE / UNVERIFIED]
EXPLANATION: [1-2 sentence explanation citing what the sources say]
"""

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": prompt}]
    )
    text = response.choices[0].message.content.strip()

    # Parse the response
    verdict = "UNVERIFIED"
    explanation = text
    for line in text.split("\n"):
        if line.startswith("VERDICT:"):
            verdict = line.replace("VERDICT:", "").strip()
        elif line.startswith("EXPLANATION:"):
            explanation = line.replace("EXPLANATION:", "").strip()

    return {
        "claim": claim,
        "verdict": verdict,
        "explanation": explanation,
        "sources": [{"title": r["title"], "url": r["url"]} for r in search_results],
    }