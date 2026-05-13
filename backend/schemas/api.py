# ─────────────────────────────────────────────
# schemas/api.py — API Request/Response Models
# ─────────────────────────────────────────────

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class QueryRequest(BaseModel):
    query: str = Field(..., description="The user's research question")
    force_workflow: Optional[str] = Field(None, description="Optional: 'langgraph' or 'crewai' to bypass router")

class QueryResponse(BaseModel):
    query: str
    workflow_used: str = Field(..., description="Which workflow handled the query ('langgraph' or 'crewai')")
    final_report: str = Field(..., description="The markdown formatted research report")
    search_results: List[Dict[str, Any]] = Field(default_factory=list, description="Raw search sources and links")
    fact_check: Dict[str, Any] = Field(default_factory=dict, description="Fact-checker's verdict and confidence score")
    errors: List[str] = Field(default_factory=list)
