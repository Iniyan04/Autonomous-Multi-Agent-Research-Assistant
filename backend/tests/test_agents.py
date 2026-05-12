# ─────────────────────────────────────────────
# tests/test_agents.py
# US-03, 04, 05: Test All Agents
# ─────────────────────────────────────────────

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from workflows.research_workflow import run_pipeline


def test_full_pipeline():
    """
    End-to-end test for all 3 agents running together.
    US-03: Research Agent
    US-04: Summarization Agent
    US-05: Fact-Check Agent
    """
    print("\n" + "="*60)
    print("  Running Full Multi-Agent Pipeline Test")
    print("="*60)

    result = run_pipeline("What is machine learning?")

    # ── US-03: Research Agent ──────────────────
    print("\n--- US-03: Research Agent ---")
    assert isinstance(result["search_results"], list), "search_results should be a list"
    assert len(result["search_results"]) > 0, "search_results should not be empty"
    print(f" Found {len(result['search_results'])} search results")

    # ── US-04: Summarization Agent ─────────────
    print("\n--- US-04: Summarization Agent ---")
    assert isinstance(result["summary"], str), "summary should be a string"
    assert len(result["summary"]) > 0, "summary should not be empty"
    print(f" Summary generated ({len(result['summary'])} chars)")
    print(f"   Preview: {result['summary'][:150]}...")

    # ── US-05: Fact-Check Agent ────────────────
    print("\n--- US-05: Fact-Check Agent ---")
    assert isinstance(result["fact_check"], dict), "fact_check should be a dict"
    assert "overall_verdict" in result["fact_check"], "fact_check should have overall_verdict"
    print(f" Fact check complete")
    print(f"   Verdict:    {result['fact_check'].get('overall_verdict')}")
    print(f"   Confidence: {result['fact_check'].get('confidence_score')}%")

    # ── Errors ────────────────────────────────
    print("\n--- Errors ---")
    if result["errors"]:
        print(f"  Errors: {result['errors']}")
    else:
        print("✅ No errors")

    print("\n" + "="*60)
    print("   All agent tests passed!")
    print("="*60 + "\n")


if __name__ == "__main__":
    test_full_pipeline()