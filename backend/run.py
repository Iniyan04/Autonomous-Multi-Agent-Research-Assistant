# ─────────────────────────────────────────────
# run.py — Backend Entry Point
# Start the FastAPI server
# ─────────────────────────────────────────────

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config.settings import validate_config, API_HOST, API_PORT, DEBUG

# Validate API keys on startup
validate_config()

app = FastAPI(
    title="Autonomous Multi-Agent Research Assistant",
    description="Multi-agent AI system using Groq + LangGraph + CrewAI",
    version="1.0.0"
)

# Allow React frontend (Vite) to talk to this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

from schemas.api import QueryRequest, QueryResponse
from workflows.router import route_query
from workflows.research_workflow import run_pipeline as run_langgraph
from workflows.crewai_workflow import run_crewai_pipeline
from utils.file_exporter import save_report_to_html

@app.get("/")
def root():
    return {"message": "Multi-Agent Research Assistant API is running."}

@app.post("/api/research", response_model=QueryResponse)
def research_endpoint(req: QueryRequest):
    query = req.query
    
    # 1. Route the query
    workflow = req.force_workflow if req.force_workflow else route_query(query)
    
    if workflow == "crewai":
        # Run deep-dive autonomous agents
        report = run_crewai_pipeline(query)
        # Export to HTML
        save_report_to_html(query, report)
        
        return QueryResponse(
            query=query,
            workflow_used="crewai",
            final_report=report,
            search_results=[], # CrewAI encapsulates state natively, so we only return the final report
            fact_check={"overall_verdict": "Verified by CrewAI Fact-Checker Agent"},
            errors=[]
        )
    else:
        # Run fast LangGraph pipeline
        state = run_langgraph(query)
        report = state.get("final_report", "")
        # Export to HTML
        if report:
            save_report_to_html(query, report)
            
        return QueryResponse(
            query=query,
            workflow_used="langgraph",
            final_report=report,
            search_results=state.get("search_results", []),
            fact_check=state.get("fact_check", {}),
            errors=state.get("errors", [])
        )


if __name__ == "__main__":
    uvicorn.run("run:app", host=API_HOST, port=API_PORT, reload=DEBUG)