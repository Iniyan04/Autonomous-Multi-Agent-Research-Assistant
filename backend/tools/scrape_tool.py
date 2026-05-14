# ─────────────────────────────────────────────
# tools/scrape_tool.py — Webpage Scraper
# US-07: Used by Fact-Check Agent
# ─────────────────────────────────────────────

from langchain_core.tools import tool
import httpx
from bs4 import BeautifulSoup
import re

@tool("fetch_webpage_content")
def fetch_webpage_content(url: str) -> str:
    """
    Fetch the text content of a webpage given its URL.
    Useful for reading the full details of an article or source.
    """
    try:
        # Use httpx which is already in requirements.txt
        response = httpx.get(url, timeout=10.0)
        response.raise_for_status()
        
        # Simple extraction using basic parsing since BS4 might not be explicitly installed,
        # but langchain-community usually pulls it in. 
        # We will do a safe parse.
        html = response.text
        
        try:
            soup = BeautifulSoup(html, "html.parser")
            text = soup.get_text(separator=' ', strip=True)
        except Exception:
            # Fallback if BeautifulSoup is missing
            text = re.sub(r'<[^>]+>', ' ', html)
            text = re.sub(r'\s+', ' ', text).strip()
            
        # Truncate to avoid blowing up the LLM context window
        return text[:3000]
    except Exception as e:
        return f"Error fetching webpage: {str(e)}"
