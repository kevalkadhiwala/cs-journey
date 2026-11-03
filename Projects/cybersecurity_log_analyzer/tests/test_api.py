import pytest

pytest.importorskip("fastapi")
pytest.importorskip("httpx")

from fastapi.testclient import TestClient  # noqa: E402

from app import config  # noqa: E402
from app.api import app  # noqa: E402


@pytest.fixture
def client(loaded_db, monkeypatch):
    monkeypatch.setattr(config, "DATABASE_PATH", loaded_db.database_name)
    return TestClient(app)


def test_home(client):
    assert client.get("/").json()["message"].startswith("Cybersecurity Log Analyzer")


def test_statistics(client):
    assert client.get("/statistics").json() == {
        "total_events": 11, "failed_logins": 7,
        "successful_logins": 3, "suspicious_ips": 2,
    }


def test_suspicious_ips(client):
    data = client.get("/suspicious-ips").json()
    assert data["count"] == 2


def test_high_risk(client):
    data = client.get("/high-risk").json()
    assert data["count"] == 1
    assert data["high_risk_ips"][0]["ip_address"] == "192.168.1.99"


def test_events_filter(client):
    data = client.get("/events", params={"ip_address": "192.168.1.77"}).json()
    assert data["count"] == 3


def test_dashboard_is_served(client):
    response = client.get("/dashboard")
    assert response.status_code == 200
    assert "escapeHtml" in response.text


def test_api_works_before_any_ingest(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "DATABASE_PATH", tmp_path / "empty.db")
    response = TestClient(app).get("/statistics")
    assert response.status_code == 200
    assert response.json()["total_events"] == 0


def test_cors_rejects_unknown_origins(client):
    response = client.get("/statistics", headers={"Origin": "https://evil.example"})
    assert "access-control-allow-origin" not in response.headers


def test_cors_allows_configured_origin(client):
    response = client.get("/statistics", headers={"Origin": "http://localhost:8000"})
    assert response.headers["access-control-allow-origin"] == "http://localhost:8000"
