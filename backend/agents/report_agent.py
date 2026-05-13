# ─────────────────────────────────────────────
# agents/report_agent.py
# US-06: Report Generator Agent — Full Implementation
# ─────────────────────────────────────────────

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from schemas.state import ResearchState
from llm.groq_client import get_llm
import json

# ── Prompt ────────────────────────────────────
REPORT_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are a Report Generator Agent. Your job is to compile 
    research data, summaries, and fact-checking results into a final, 
    professional, and well-formatted Markdown report.

    The report MUST include:
    - A clear, engaging Title based on the query
    - An Executive Summary
    - Detailed sections based on the summarized findings
    - A Fact-Check Verdict section (highlighting reliability, confidence score, and any flagged claims)
    - A References list at the end

    Ensure the Markdown formatting is clean, using headings (##, ###), 
    bullet points, and bold text where appropriate to make it highly readable."""),
    ("human", """Query: {query}

Summary:
{summary}

Fact-Check Results:
{fact_check}

References:
{references}

Generate the final comprehensive research report in Markdown.""")
])


def report_node(state: ResearchState) -> ResearchState:
    """
    Report Generator Agent — formats the final research report.

    Steps:
        1. Takes summary, fact_check, and search_results from state
        2. Uses Groq LLM to generate a beautifully formatted markdown report
        3. Returns final_report in state

    Populates: state['final_report']
    """
    print("\n  [Report Generator Agent] Starting report generation...")

    query          = state.get("query", "")
    summary        = state.get("summary", "")
    fact_check     = state.get("fact_check", {})
    search_results = state.get("search_results", [])
    errors         = []

    try:
        if not summary:
            print("    No summary available for report.")
            return {**state, "final_report": "No data available to generate a report.", "errors": ["Report Agent: No summary available."]}

        # Step 1: Format References
        references = "\n".join([
            f"- [{r['title']}]({r['url']})"
            for r in search_results
        ])

        # Step 2: Format Fact-Check data for prompt
        fact_check_formatted = json.dumps(fact_check, indent=2)

        # Step 3: Use Groq LLM to generate the report
        print("   Drafting final report with Groq LLM...")
        llm   = get_llm()
        chain = REPORT_PROMPT | llm | StrOutputParser()

        report = chain.invoke({
            "query":      query,
            "summary":    summary,
            "fact_check": fact_check_formatted,
            "references": references
        })

        print("    [Report Generator Agent] Complete.\n")
        return {**state, "final_report": report, "errors": errors}

    except Exception as e:
        error_msg = f"Report Generator Agent Error: {str(e)}"
        print(f"    {error_msg}")
        return {**state, "final_report": "", "errors": [error_msg]}
