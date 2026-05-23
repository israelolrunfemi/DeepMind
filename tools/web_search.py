"""Web search tool using DuckDuckGo Instant Answer API."""

from __future__ import annotations

from typing import Any

import httpx

from config import DUCKDUCKGO_URL, WEB_SEARCH_TIMEOUT


def _related_topic_items(items: list[Any]) -> list[dict[str, str]]:
    results: list[dict[str, str]] = []
    for item in items:
        if not isinstance(item, dict):
            continue
        if "Topics" in item and isinstance(item["Topics"], list):
            results.extend(_related_topic_items(item["Topics"]))
            continue
        text = item.get("Text")
        url = item.get("FirstURL")
        if isinstance(text, str) and isinstance(url, str):
            title = text.split(" - ", maxsplit=1)[0]
            results.append({"title": title, "url": url, "snippet": text})
    return results


async def search(query: str, max_results: int = 5) -> dict[str, Any]:
    """Search DuckDuckGo and return an abstract plus related topic results."""

    try:
        async with httpx.AsyncClient(timeout=WEB_SEARCH_TIMEOUT) as client:
            response = await client.get(
                DUCKDUCKGO_URL,
                params={"q": query, "format": "json", "no_html": "1", "skip_disambig": "1"},
            )
            response.raise_for_status()
            payload = response.json()
    except httpx.HTTPError as exc:
        return {"status": "error", "error": f"DuckDuckGo request failed: {exc}"}
    except ValueError as exc:
        return {"status": "error", "error": f"DuckDuckGo returned invalid JSON: {exc}"}

    related_topics = payload.get("RelatedTopics", [])
    results = _related_topic_items(related_topics if isinstance(related_topics, list) else [])
    return {
        "status": "success",
        "abstract": payload.get("AbstractText", "") if isinstance(payload, dict) else "",
        "results": results[:max_results],
    }
