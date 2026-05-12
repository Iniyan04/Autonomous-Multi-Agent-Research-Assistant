# ─────────────────────────────────────────────
# agents/summarization_agent.py
# US-04: Summarization Agent — Full Implementation
# ─────────────────────────────────────────────

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from schemas.state import ResearchState
from llm.groq_client import get_llm


# ── Prompt ────────────────────────────────────
SUMMARIZATION_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are a Summarization Agent. Your job is to condense 
    research findings into a clear, structured summary.

    Your summary must:
    - Be well organized with clear sections
    - Highlight the most important findings
    - Be concise but comprehensive
    - Use simple, easy to understand language
    - Include key facts, figures, and insights
    - Be written in a neutral, informative tone

    Structure your summary as:
    ## Overview
    (2-3 sentence overview of the topic)

    ## Key Findings
    (bullet points of the most important facts)

    ## Important Details
    (any additional relevant context or details)
    """),
    ("human", """Query: {query}

Research Data:
{research_data}

Generate a comprehensive, well-structured summary of the above research.""")
])


def summarization_node(state: ResearchState) -> ResearchState:
    """
    Summarization Agent — condenses search results into a structured summary.

    Steps:
        1. Takes search_results from state
        2. Uses Groq LLM to generate a structured summary
        3. Stores summary back in state

    Populates: state['summary']
    """
    print("\n [Summarization Agent] Starting summarization...")

    query          = state["query"]
    search_results = state["search_results"]
    errors         = []

    try:
        if not search_results:
            print("    No search results to summarize.")
            return {**state, "summary": "No research data available to summarize.", "errors": ["Summarization Agent: No search results available."]}

        # Step 1: Combine all research content
        research_data = "\n\n".join([
            f"Source: {r['title']}\n{r.get('analysis', r['content'])}"
            for r in search_results
        ])

        # Step 2: Use Groq LLM to summarize
        print("   Generating summary with Groq LLM...")
        llm    = get_llm()
        chain  = SUMMARIZATION_PROMPT | llm | StrOutputParser()

        summary = chain.invoke({
            "query":         query,
            "research_data": research_data
        })

        print("   ✅ [Summarization Agent] Complete.\n")
        return {**state, "summary": summary, "errors": errors}

    except Exception as e:
        error_msg = f"Summarization Agent Error: {str(e)}"
        print(f"    {error_msg}")
        return {**state, "summary": "", "errors": [error_msg]}