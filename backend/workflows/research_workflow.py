# ─────────────────────────────────────────────
# workflows/research_workflow.py
# US-02: Multi-Agent Architecture — LangGraph Workflow
# ─────────────────────────────────────────────

from langgraph.graph import StateGraph, END

from schemas.state import ResearchState
from agents.research_agent import research_node
from agents.summarization_agent import summarization_node
from agents.fact_check_agent import fact_check_node
from agents.report_agent import report_node





# ── Build LangGraph Workflow ──────────────────
def build_workflow():
    """
    Constructs and compiles the multi-agent LangGraph pipeline.

    Agent Flow:
        research → summarization → fact_check → report → END
    """
    graph = StateGraph(ResearchState)

    # Register all agent nodes
    graph.add_node("research",      research_node)
    graph.add_node("summarization", summarization_node)
    graph.add_node("fact_check",    fact_check_node)
    graph.add_node("report",        report_node)

    # Define sequential flow between agents
    graph.set_entry_point("research")
    graph.add_edge("research",      "summarization")
    graph.add_edge("summarization", "fact_check")
    graph.add_edge("fact_check",    "report")
    graph.add_edge("report",        END)

    return graph.compile()


# ── Pipeline Entry Point ──────────────────────
def run_pipeline(query: str) -> ResearchState:
    """
    Main entry point — runs the full multi-agent research pipeline.

    Args:
        query: The user's research question

    Returns:
        Final ResearchState with all agent outputs populated
    """
    print(f"\n Starting research pipeline for: '{query}'\n")

    workflow = build_workflow()

    # Initialize state with empty values
    initial_state: ResearchState = {
        "query":          query,
        "search_results": [],
        "summary":        "",
        "fact_check":     {},
        "final_report":   "",
        "errors":         []
    }

    final_state = workflow.invoke(initial_state)
    print("\nPipeline complete.\n")
    return final_state