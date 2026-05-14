from fastapi.testclient import TestClient

import run


client = TestClient(run.app)


def test_health_check():
    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_workflow_options():
    response = client.get("/api/workflows")
    data = response.json()

    assert response.status_code == 200
    assert data["default"] == "auto"
    assert {workflow["id"] for workflow in data["workflows"]} == {"auto", "langgraph", "crewai"}


def test_research_rejects_empty_query():
    response = client.post("/api/research", json={"query": "   ", "force_workflow": "langgraph"})

    assert response.status_code == 400
    assert response.json()["detail"] == "Query cannot be empty."


def test_research_langgraph_response(monkeypatch):
    def fake_run_langgraph(query):
        return {
            "query": query,
            "search_results": [
                {
                    "title": "Example source",
                    "url": "https://example.com",
                    "content": "Example content",
                }
            ],
            "summary": "Short summary",
            "fact_check": {"overall_verdict": "RELIABLE", "confidence_score": 95},
            "final_report": "# Report\n\nUseful findings.",
            "errors": [],
        }

    monkeypatch.setattr(run, "run_langgraph", fake_run_langgraph)
    monkeypatch.setattr(run, "save_report_to_html", lambda query, report: "reports/mock.html")

    response = client.post(
        "/api/research",
        json={"query": "  What is AI?  ", "force_workflow": "langgraph"},
    )
    data = response.json()

    assert response.status_code == 200
    assert data["query"] == "What is AI?"
    assert data["workflow_used"] == "langgraph"
    assert data["fact_check"]["overall_verdict"] == "RELIABLE"
    assert len(data["search_results"]) == 1


def test_research_rejects_unknown_workflow():
    response = client.post(
        "/api/research",
        json={"query": "What is AI?", "force_workflow": "unknown"},
    )

    assert response.status_code == 400
    assert "force_workflow" in response.json()["detail"]
