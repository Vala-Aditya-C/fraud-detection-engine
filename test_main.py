import pytest
from fastapi.testclient import TestClient
from main import app

@pytest.fixture
def client():
    # Enforces FastAPI startup events (database creation) during testing
    with TestClient(app) as c:
        yield c

def test_health_check(client):
    """Verify that health check returns 200 OK and model is loaded."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
    assert response.json()["model_loaded"] is True

def test_evaluate_transaction_approved(client):
    """Test a low-risk transaction scenario."""
    payload = {
        "user_id": "TEST_USER_01",
        "amount": 20.0,
        "time_delta": 150.0,
        "geo_distance": 2.0,
        "is_foreign": 0
    }
    response = client.post("/v1/evaluate-transaction", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ["APPROVED", "REVIEW", "BLOCKED"]
    assert "risk_score" in data
    assert "latency_ms" in data

def test_evaluate_transaction_high_risk(client):
    """Test a high-risk transaction scenario."""
    payload = {
        "user_id": "TEST_USER_02",
        "amount": 950.0,
        "time_delta": 0.5,
        "geo_distance": 350.0,
        "is_foreign": 1
    }
    response = client.post("/v1/evaluate-transaction", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "BLOCKED"
    assert data["risk_score"] >= 0.70

def test_invalid_payload(client):
    """Verify pydantic data validation rejects bad types."""
    payload = {
        "user_id": "TEST_USER_03",
        "amount": "invalid_amount_string"
    }
    response = client.post("/v1/evaluate-transaction", json=payload)
    assert response.status_code == 422