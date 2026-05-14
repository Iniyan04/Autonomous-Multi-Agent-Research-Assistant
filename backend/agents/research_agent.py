# ─────────────────────────────────────────────
# agents/research_agent.py
# US-03: Research Agent — Full Implementation (with Tool Calling)
# ─────────────────────────────────────────────

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
    Research Agent — autonomously searches the web and extracts relevant information.
    """
    print("\n [Research Agent] Starting autonomous research...")

    query = state["query"]
    errors = []

    try:
        llm = get_llm()
        
        # Step 1: Bind tools to the LLM so it can autonomously decide queries
        print(f"   Agent is deciding search strategy for: '{query}'")
        llm_with_tools = llm.bind_tools([search_web])
        
        # Prompt LLM to use the tool
        tool_prompt = f"Use the search tool to find information about this query: {query}. You may generate the best possible search string."
        tool_response = llm_with_tools.invoke(tool_prompt)
        
        raw_results = []
        if tool_response.tool_calls:
            for tool_call in tool_response.tool_calls:
                print(f"    Executing tool: {tool_call['name']} with args {tool_call['args']}")
                # Execute the tool
                if tool_call['name'] == 'search_web':
                    # Extract the query from arguments
                    search_arg = tool_call['args'].get('query', query)
                    call_results = search_web.invoke({"query": search_arg})
                    raw_results.extend(call_results)
        else:
            # Fallback if the LLM decided not to use the tool
            print("    LLM decided not to use the tool. Forcing search...")
            raw_results = search_web.invoke({"query": query})

        if not raw_results:
            print("    No search results found.")
            return {**state, "search_results": [], "errors": ["Research Agent: No search results found."]}

        print(f"    Found {len(raw_results)} results.")

        # Step 2: Format results for LLM analysis
        formatted_results = "\n\n".join([
            f"Source {i+1}: {r.get('title', '')}\nURL: {r.get('url', '')}\nContent: {r.get('content', '')}"
            for i, r in enumerate(raw_results) if isinstance(r, dict)
        ])

        # Step 3: Use Groq LLM to extract relevant information
        print("   Analyzing results with Groq LLM...")
        chain = RESEARCH_PROMPT | llm | StrOutputParser()

        analysis = chain.invoke({
            "query": query,
            "search_results": formatted_results
        })

        # Step 4: Store structured results in state
        search_results = [
            {
                "title":    r.get("title", "Unknown"),
                "url":      r.get("url", "#"),
                "content":  r.get("content", ""),
                "analysis": analysis  # LLM extracted insights
            }
            for r in raw_results if isinstance(r, dict)
        ]

        print("    [Research Agent] Complete.\n")
        return {**state, "search_results": search_results, "errors": errors}

    except Exception as e:
        error_msg = f"Research Agent Error: {str(e)}"
        print(f"    {error_msg}")
        return {**state, "search_results": [], "errors": [error_msg]}