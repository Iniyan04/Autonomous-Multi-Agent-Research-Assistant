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

    The report MUST use this exact structure:
    # Report Title

    ## Executive Summary
    2-3 concise sentences.

    ## Key Findings
    4-6 bullet points. Each bullet must start on its own line.

    ## Timeline / Background
    Short paragraphs or bullets when useful.

    ## Fact-Check Verdict
    Highlight reliability, confidence score, and flagged claims.

    ## References
    Bullet list of source titles and URLs.

    Ensure the Markdown formatting is clean, using headings (##, ###), 
    bullet points, and bold text where appropriate to make it highly readable.
    Put blank lines between every heading, paragraph, and list. Do not put
    multiple headings or bullets on the same line."""),
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
