# ─────────────────────────────────────────────
# tools/search_tool.py — Tavily Search Wrapper
# US-03: Used by Research Agent
# ─────────────────────────────────────────────

from tavily import TavilyClient
from config.settings import TAVILY_API_KEY, TAVILY_MAX_RESULTS


def search_web(query: str) -> list[dict]:
    """
    Search the web using Tavily API (free tier).

    Args:
        query: Search query string

    Returns:
        List of dicts → { title, url, content }
    """
    try:
        client = TavilyClient(api_key=TAVILY_API_KEY)
        response = client.search(
            query=query,
            max_results=TAVILY_MAX_RESULTS,
            search_depth="advanced"
        )
        results = response.get("results", [])
        return [
            {
                "title":   r.get("title", ""),
                "url":     r.get("url", ""),
                "content": r.get("content", "")
            }
            for r in results
        ]
    except Exception as e:
        print(f"[search_tool] ❌ Search failed: {e}")
        return []