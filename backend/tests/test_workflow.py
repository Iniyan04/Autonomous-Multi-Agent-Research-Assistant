# ─────────────────────────────────────────────
# tests/test_workflow.py
# US-02: Test Multi-Agent Workflow
# ─────────────────────────────────────────────

from workflows.research_workflow import run_pipeline


def test_pipeline_runs():
    """Test that the pipeline runs end to end with placeholder agents."""
    result = run_pipeline("What is artificial intelligence?")

    assert result["query"] == "What is artificial intelligence?"
    assert isinstance(result["search_results"], list)
    assert isinstance(result["summary"], str)
    assert isinstance(result["fact_check"], dict)
    assert isinstance(result["final_report"], str)
    assert isinstance(result["errors"], list)

    print("✅ US-02 workflow test passed!")


if __name__ == "__main__":
    test_pipeline_runs()