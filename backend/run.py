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

@app.get("/")
def root():
    return {"message": "Multi-Agent Research Assistant API is running."}


if __name__ == "__main__":
    uvicorn.run("run:app", host=API_HOST, port=API_PORT, reload=DEBUG)