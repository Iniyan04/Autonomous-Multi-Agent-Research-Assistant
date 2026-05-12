# ─────────────────────────────────────────────
# agents/research_agent.py
# US-03: Research Agent — Full Implementation
# ─────────────────────────────────────────────

from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from schemas.state import ResearchState
from tools.search_tool import search_web
from llm.groq_client import get_llm


# ── Prompt ────────────────────────────────────
RESEARCH_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are a Research Agent. Your job is to analyze 
    search results and extract the most relevant, accurate information 
    related to the user's query.
    
    Given the search results, identify and organize:
    - Key facts and findings
    - Important data points
    - Relevant context
    
    Be thorough but focused. Only include information directly 
    relevant to the query."""),
    ("human", """Query: {query}
    
Search Results:
{search_results}

Extract and organize the most relevant information from these results.""")
])


def research_node(state: ResearchState) -> ResearchState:
    """
    Research Agent — searches the web and extracts relevant information.

    Steps:
        1. Takes user query from state
        2. Searches the web using Tavily
        3. Uses Groq LLM to extract relevant info from results
        4. Stores results back in state

    Populates: state['search_results']
    """
    print("\n [Research Agent] Starting research...")

    query = state["query"]
    errors = []

    try:
        # Step 1: Search the web using Tavily
        print(f"   Searching web for: '{query}'")
        raw_results = search_web(query)

        if not raw_results:
            print("    No search results found.")
            return {**state, "search_results": [], "errors": ["Research Agent: No search results found."]}

        print(f"    Found {len(raw_results)} results.")

        # Step 2: Format results for LLM
        formatted_results = "\n\n".join([
            f"Source {i+1}: {r['title']}\nURL: {r['url']}\nContent: {r['content']}"
            for i, r in enumerate(raw_results)
        ])

        # Step 3: Use Groq LLM to extract relevant information
        print("   Analyzing results with Groq LLM...")
        llm = get_llm()
        chain = RESEARCH_PROMPT | llm | StrOutputParser()

        analysis = chain.invoke({
            "query": query,
            "search_results": formatted_results
        })

        # Step 4: Store structured results in state
        search_results = [
            {
                "title":    r["title"],
                "url":      r["url"],
                "content":  r["content"],
                "analysis": analysis  # LLM extracted insights
            }
            for r in raw_results
        ]

        print("    [Research Agent] Complete.\n")
        return {**state, "search_results": search_results, "errors": errors}

    except Exception as e:
        error_msg = f"Research Agent Error: {str(e)}"
        print(f"    {error_msg}")
        return {**state, "search_results": [], "errors": [error_msg]}