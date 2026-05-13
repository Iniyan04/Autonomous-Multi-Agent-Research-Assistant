# ─────────────────────────────────────────────
# workflows/router.py — Smart Query Router
# ─────────────────────────────────────────────

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from llm.groq_client import get_llm
import json
import re

ROUTER_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are an intelligent Query Router. Your job is to classify an incoming research query 
    to determine the most appropriate multi-agent workflow.

    We have two workflows:
    1. 'langgraph': Best for simple, straightforward questions, quick factual lookups, or single-topic summaries.
    2. 'crewai': Best for highly complex, multi-faceted, analytical, or deep-dive research requests that require autonomous agent collaboration.

    Analyze the complexity of the query.
    Return ONLY a valid JSON object in this exact format:
    {{
        "workflow": "langgraph" | "crewai",
        "reasoning": "brief explanation"
    }}
    """),
    ("human", "Query: {query}")
])

def route_query(query: str) -> str:
    """
    Analyzes the query and returns 'langgraph' or 'crewai'.
    Falls back to 'langgraph' if parsing fails.
    """
    print(f"\n[Router] Analyzing query complexity: '{query}'")
    try:
        llm = get_llm()
        chain = ROUTER_PROMPT | llm | StrOutputParser()
        
        result = chain.invoke({"query": query})
        
        # Clean up response in case LLM adds markdown or extra text
        json_match = re.search(r'\{.*\}', result, re.DOTALL)
        if json_match:
            parsed = json.loads(json_match.group())
        else:
            parsed = json.loads(result)
            
        workflow = parsed.get("workflow", "langgraph")
        reasoning = parsed.get("reasoning", "No reason provided")
        
        # Ensure it's one of the valid options
        if workflow not in ["langgraph", "crewai"]:
            workflow = "langgraph"
            
        print(f"  -> Selected workflow: {workflow.upper()} (Reason: {reasoning})")
        return workflow

    except Exception as e:
        print(f"  -> Router failed ({str(e)}), defaulting to LANGGRAPH")
        return "langgraph"
