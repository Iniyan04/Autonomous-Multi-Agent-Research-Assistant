# ─────────────────────────────────────────────
# config/settings.py — Centralized Configuration
# ─────────────────────────────────────────────

import os
from dotenv import load_dotenv

load_dotenv()

# ── Groq LLM (FREE) ───────────────────────────
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL   = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
MAX_TOKENS   = int(os.getenv("MAX_TOKENS", 2048))

# ── Tavily Search (FREE) ──────────────────────
TAVILY_API_KEY     = os.getenv("TAVILY_API_KEY")
TAVILY_MAX_RESULTS = int(os.getenv("TAVILY_MAX_RESULTS", 5))

# ── FastAPI ───────────────────────────────────
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", 8000))
DEBUG    = os.getenv("DEBUG", "True") == "True"

# ── Paths ─────────────────────────────────────
BASE_DIR    = os.path.dirname(os.path.dirname(__file__))
REPORTS_DIR = os.path.join(BASE_DIR, "reports")
LOGS_DIR    = os.path.join(BASE_DIR, "logs")

os.makedirs(REPORTS_DIR, exist_ok=True)
os.makedirs(LOGS_DIR, exist_ok=True)


# ── Validation ────────────────────────────────
def validate_config():
    missing = []
    if not GROQ_API_KEY:
        missing.append("GROQ_API_KEY")
    if not TAVILY_API_KEY:
        missing.append("TAVILY_API_KEY")
    if missing:
        raise EnvironmentError(
            f"\n Missing environment variables: {', '.join(missing)}\n"
            f"   → Fill in your free API keys in the .env file.\n"
            f"   → Groq:   https://console.groq.com\n"
            f"   → Tavily: https://app.tavily.com\n"
        )