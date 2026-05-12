# ─────────────────────────────────────────────
# llm/groq_client.py — Groq LLM Client
# ─────────────────────────────────────────────

from langchain_groq import ChatGroq
from config.settings import GROQ_API_KEY, GROQ_MODEL, MAX_TOKENS


def get_llm() -> ChatGroq:
    """
    Returns a configured Groq LLM instance.
    Model : llama-3.3-70b-versatile (free tier)
    Temp  : 0.3 — keeps responses factual
    """
    return ChatGroq(
        api_key=GROQ_API_KEY,
        model=GROQ_MODEL,
        max_tokens=MAX_TOKENS,
        temperature=0.3,
    )