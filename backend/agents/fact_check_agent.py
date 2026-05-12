# ─────────────────────────────────────────────
# agents/fact_check_agent.py
# US-05: Fact-Check Agent — Full Implementation
# ─────────────────────────────────────────────

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from schemas.state import ResearchState
from llm.groq_client import get_llm
import json
import re


# ── Prompt ────────────────────────────────────
FACT_CHECK_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are a Fact-Check Agent. Your job is to validate 
    the accuracy of a research summary by cross-referencing it against 
    the original source data.

    Analyze each key claim in the summary and:
    - Verify if it is supported by the source data
    - Flag anything that seems inaccurate, exaggerated, or unsupported
    - Rate the overall reliability of the summary

    You MUST respond with ONLY a valid JSON object in this exact format:
    {{
        "overall_verdict": "RELIABLE | MOSTLY RELIABLE | UNRELIABLE",
        "confidence_score": <number between 0 and 100>,
        "verified_claims": ["claim 1", "claim 2"],
        "flagged_claims": ["claim 1 (reason)", "claim 2 (reason)"],
        "corrections": ["correction 1", "correction 2"],
        "recommendation": "brief recommendation"
    }}

    Return ONLY the JSON. No explanation, no markdown, no extra text."""),
    ("human", """Query: {query}

Original Source Data:
{source_data}

Summary to Fact-Check:
{summary}

Validate the summary against the source data and return the JSON result.""")
])


def fact_check_node(state: ResearchState) -> ResearchState:
    """
    Fact-Check Agent — validates the summary against original source data.

    Steps:
        1. Takes summary and search_results from state
        2. Uses Groq LLM to cross-validate claims
        3. Returns structured fact-check report in state

    Populates: state['fact_check']
    """
    print("\n  [Fact-Check Agent] Starting fact check...")

    query          = state["query"]
    summary        = state["summary"]
    search_results = state["search_results"]
    errors         = []

    try:
        if not summary:
            print("    No summary to fact check.")
            return {**state, "fact_check": {"overall_verdict": "UNRELIABLE", "confidence_score": 0}, "errors": ["Fact-Check Agent: No summary available."]}

        # Step 1: Prepare source data for comparison
        source_data = "\n\n".join([
            f"Source: {r['title']}\nURL: {r['url']}\nContent: {r['content']}"
            for r in search_results
        ])

        # Step 2: Use Groq LLM to fact-check
        print("   Cross-validating claims with Groq LLM...")
        llm   = get_llm()
        chain = FACT_CHECK_PROMPT | llm | StrOutputParser()

        result = chain.invoke({
            "query":       query,
            "source_data": source_data,
            "summary":     summary
        })

        # Step 3: Parse JSON response
        try:
            # Clean up response in case LLM adds extra text
            json_match = re.search(r'\{.*\}', result, re.DOTALL)
            if json_match:
                fact_check = json.loads(json_match.group())
            else:
                fact_check = json.loads(result)
        except json.JSONDecodeError:
            print("    Could not parse JSON, using raw response.")
            fact_check = {"overall_verdict": "UNKNOWN", "raw_response": result}

        print(f"   Verdict: {fact_check.get('overall_verdict', 'UNKNOWN')} | Confidence: {fact_check.get('confidence_score', 'N/A')}%")
        print("    [Fact-Check Agent] Complete.\n")
        return {**state, "fact_check": fact_check, "errors": errors}

    except Exception as e:
        error_msg = f"Fact-Check Agent Error: {str(e)}"
        print(f"    {error_msg}")
        return {**state, "fact_check": {}, "errors": [error_msg]}