# ─────────────────────────────────────────────
# schemas/state.py — Shared LangGraph State
# US-02: Multi-Agent Architecture
# ─────────────────────────────────────────────

from typing import TypedDict, Annotated
import operator


class ResearchState(TypedDict):
    """
    The single state object that flows through every agent node.

    Flow:
        research_agent → summarization_agent → fact_check_agent → report_agent

    Each agent reads from this state and writes its output back into it.
    """
    query:          str                            # Original user query
    search_results: list[dict]                     # Raw web results      — Research Agent
    summary:        str                            # Condensed content    — Summarization Agent
    fact_check:     dict                           # Validation results   — Fact-Check Agent
    final_report:   str                            # Final report         — Report Generator
    errors:         Annotated[list, operator.add]  # Accumulated errors across all agents