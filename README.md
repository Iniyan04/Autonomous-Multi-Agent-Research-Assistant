# Autonomous Multi-Agent Research Assistant

An AI research assistant that routes user questions through LangGraph or CrewAI agents, searches the web with Tavily, reasons with Groq-hosted LLMs, fact-checks findings, and returns a structured Markdown report through a FastAPI-served web UI.

## Features

- Automatic workflow routing for fast research or deeper CrewAI collaboration
- Static frontend served directly by FastAPI at `/app`
- Groq LLM integration with token and context safety caps
- Tavily-powered web search with concise source extraction
- Structured Markdown report output with source references
- Docker and Docker Compose support for local runs
- Azure-ready container deployment

## Project Structure

```text
Autonomous-Multi-Agent-Research-Assistant/
├── backend/
│   ├── agents/                 # LangGraph agent nodes
│   ├── config/                 # Environment and runtime settings
│   ├── llm/                    # Groq client setup
│   ├── schemas/                # API and workflow state models
│   ├── tests/                  # Backend API/workflow tests
│   ├── tools/                  # Tavily search and webpage scraping tools
│   ├── utils/                  # Report export helpers
│   ├── workflows/              # Router, LangGraph, and CrewAI workflows
│   ├── .env.example            # Environment variable template
│   ├── requirements.txt        # Python dependencies
│   └── run.py                  # FastAPI application entry point
├── frontend/
│   ├── app.js                  # Browser app logic and report rendering
│   ├── index.html              # Static UI shell
│   └── styles.css              # App styling
├── .dockerignore
├── .gitignore
├── Dockerfile
├── docker-compose.yml
└── README.md
```

## Environment Variables

Create `backend/.env` from `backend/.env.example`:

```powershell
Copy-Item backend/.env.example backend/.env
```

Required values:

```text
GROQ_API_KEY=your_groq_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here
```

Common optional values:

```text
GROQ_MODEL=llama-3.3-70b-versatile
MAX_TOKENS=2048
MAX_CONTEXT_CHARS=12000
CREWAI_VERBOSE=False
TAVILY_MAX_RESULTS=5
DEBUG=False
API_HOST=0.0.0.0
API_PORT=8000
```

Never commit `backend/.env`. For Docker, pass it at runtime. For Azure, configure these as application settings or secrets.

## Run Locally

From the project root:

```powershell
.\.venv\Scripts\activate
cd backend
python run.py
```

Open:

```text
http://localhost:8000/app
```

API docs:

```text
http://localhost:8000/docs
```

## Run With Docker

Build and run manually:

```powershell
docker build -t research-assistant .
docker run --env-file backend/.env -p 8000:8000 research-assistant
```

Or run with Docker Compose:

```powershell
docker compose up --build
```

Open:

```text
http://localhost:8000/app
```

Stop Compose:

```powershell
docker compose down
```

## Azure Deployment

This app can be deployed as a single container. A typical flow is:

```powershell
az login
az group create --name research-assistant-rg --location centralindia
az acr create --resource-group research-assistant-rg --name <unique-acr-name> --sku Basic
az acr build --registry <unique-acr-name> --image research-assistant:latest .
```

Deploy the image to Azure Container Apps or another Azure container service, expose target port `8000`, and set the required environment variables in Azure. Do not upload `backend/.env`.

The backend also supports a cloud-provided `PORT` value when `API_PORT` is not set.

## Test

From the project root:

```powershell
cd backend
python -m pytest -q
```

Some workflow tests may call external APIs, so valid Groq/Tavily keys and internet access can be required.

## API Endpoints

- `GET /` - basic API status
- `GET /app` - frontend research console
- `GET /api/health` - container/app health check
- `GET /api/workflows` - available workflow options
- `POST /api/research` - run the selected or auto-routed research workflow

## Notes

- `backend/reports/` and `backend/logs/` are generated at runtime and ignored by Git.
- `docker-compose.yml` mounts reports and logs so local Docker output remains available on the host.
- CrewAI output is capped and summarized to avoid Groq token-limit errors.
