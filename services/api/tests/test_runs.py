from fastapi.testclient import TestClient
from app.main import app


client = TestClient(app)


def test_health() -> None:
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_create_run() -> None:
    session = client.post("/api/onboarding/session/start", json={"locale": "en"}).json()
    session_id = session["session_id"]
    client.post(
        f"/api/onboarding/session/{session_id}/answer",
        json={"question_id": "industry", "answer": "dentist"},
    )
    client.post(
        f"/api/onboarding/session/{session_id}/answer",
        json={"question_id": "primary_goal", "answer": "bookings"},
    )
    client.post(
        f"/api/onboarding/session/{session_id}/answer",
        json={"question_id": "primary_channel", "answer": "whatsapp"},
    )
    client.post(f"/api/onboarding/session/{session_id}/finalize")
    response = client.post(
        "/api/runs", json={"agent_type": "demo", "inputs": {"task": "ping"}}
    )
    assert response.status_code == 200
    body = response.json()
    assert "run_id" in body


def test_events_stream() -> None:
    session = client.post("/api/onboarding/session/start", json={"locale": "en"}).json()
    session_id = session["session_id"]
    client.post(
        f"/api/onboarding/session/{session_id}/answer",
        json={"question_id": "industry", "answer": "dentist"},
    )
    client.post(
        f"/api/onboarding/session/{session_id}/answer",
        json={"question_id": "primary_goal", "answer": "bookings"},
    )
    client.post(
        f"/api/onboarding/session/{session_id}/answer",
        json={"question_id": "primary_channel", "answer": "whatsapp"},
    )
    client.post(f"/api/onboarding/session/{session_id}/finalize")
    run = client.post("/api/runs", json={"agent_type": "demo", "inputs": {"task": "ping"}}).json()
    with client.stream("GET", f"/api/runs/{run['run_id']}/events") as response:
        assert response.status_code == 200
