import os

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from config.settings import API_HOST, API_PORT, DEBUG, validate_config
from schemas.api import QueryRequest, QueryResponse
from utils.file_exporter import save_report_to_html
from workflows.crewai_workflow import run_crewai_pipeline
from workflows.research_workflow import run_pipeline as run_langgraph
from workflows.router import route_query


validate_config()

app = FastAPI(
    title="Autonomous Multi-Agent Research Assistant",
    description="Multi-agent AI system using Groq, LangGraph, and CrewAI",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:5500",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5500",
    ],
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")
VALID_WORKFLOWS = {"langgraph", "crewai"}

if os.path.isdir(FRONTEND_DIR):
    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="frontend-static")


@app.get("/")
def root():
    return {"message": "Multi-Agent Research Assistant API is running."}


@app.get("/app", include_in_schema=False)
def frontend_app():
    index_path = os.path.join(FRONTEND_DIR, "index.html")
    if not os.path.exists(index_path):
        raise HTTPException(status_code=404, detail="Frontend app is not available.")
    return FileResponse(index_path)


@app.get("/api/health")
def health_check():
    return {
        "status": "ok",
        "service": "Autonomous Multi-Agent Research Assistant",
        "version": app.version,
    }


@app.get("/api/workflows")
def workflow_options():
    return {
        "default": "auto",
        "workflows": [
            {
                "id": "auto",
                "name": "Auto Router",
                "description": "Selects LangGraph or CrewAI based on query complexity.",
            },
            {
                "id": "langgraph",
                "name": "Fast Research",
                "description": "Sequential LangGraph workflow for focused research questions.",
            },
            {
                "id": "crewai",
                "name": "Deep Dive",
                "description": "CrewAI collaboration workflow for complex research tasks.",
            },
        ],
    }


@app.post("/api/research", response_model=QueryResponse)
def research_endpoint(req: QueryRequest):
    query = req.query.strip()
    if not query:
        raise HTTPException(status_code=400, detail="Query cannot be empty.")

    workflow = req.force_workflow.strip().lower() if req.force_workflow else route_query(query)
    if workflow == "auto":
        workflow = route_query(query)
    if workflow not in VALID_WORKFLOWS:
        raise HTTPException(status_code=400, detail="force_workflow must be 'auto', 'langgraph', or 'crewai'.")

    if workflow == "crewai":
        report = run_crewai_pipeline(query)
        save_report_to_html(query, report)

        return QueryResponse(
            query=query,
            workflow_used="crewai",
            final_report=report,
            search_results=[],
            fact_check={"overall_verdict": "Verified by CrewAI Fact-Checker Agent"},
            errors=[],
        )

    state = run_langgraph(query)
    report = state.get("final_report", "")
    if report:
        save_report_to_html(query, report)

    return QueryResponse(
        query=query,
        workflow_used="langgraph",
        final_report=report,
        search_results=state.get("search_results", []),
        fact_check=state.get("fact_check", {}),
        errors=state.get("errors", []),
    )


if __name__ == "__main__":
    uvicorn.run("run:app", host=API_HOST, port=API_PORT, reload=DEBUG)
