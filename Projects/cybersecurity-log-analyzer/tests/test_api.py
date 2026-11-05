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
        "total_events": 14, "failed_logins": 10,
        "successful_logins": 3, "suspicious_ips": 2,
        "targeted_accounts": 1,
    }


def test_suspicious_ips(client):
    data = client.get("/suspicious-ips").json()
    assert data["count"] == 2


def test_high_risk(client):
    data = client.get("/high-risk").json()
    assert data["count"] == 1
    assert data["high_risk_ips"][0]["ip_address"] == "192.168.1.99"


def test_targeted_accounts(client):
    data = client.get("/targeted-accounts").json()
    assert data["count"] == 1
    assert data["targeted_accounts"][0]["username"] == "root"
    assert len(data["targeted_accounts"][0]["attacking_ips"]) == 3


def test_events_filter(client):
    data = client.get("/events", params={"ip_address": "192.168.1.77"}).json()
    assert data["count"] == 3


def test_events_date_range(client):
    data = client.get("/events", params={"start": "2026-08-18 11:00:00",
                                         "end": "2026-08-18 23:59:59"}).json()
    assert data["total"] == 5


def test_events_date_only_end_includes_whole_day(client):
    data = client.get("/events", params={"end": "2026-08-18"}).json()
    assert data["total"] == 14


def test_events_pagination(client):
    first = client.get("/events", params={"limit": 10, "offset": 0}).json()
    second = client.get("/events", params={"limit": 10, "offset": 10}).json()
    assert (first["count"], second["count"]) == (10, 4)
    assert first["total"] == second["total"] == 14


@pytest.mark.parametrize("params", [
    {"start": "18/08/2026"},
    {"end": "not-a-date"},
    {"start": "2026-08-19", "end": "2026-08-18"},
])
def test_events_rejects_bad_dates(client, params):
    response = client.get("/events", params=params)
    assert response.status_code == 400


@pytest.mark.parametrize("params", [{"limit": 0}, {"limit": 101}, {"offset": -1}])
def test_events_rejects_bad_paging(client, params):
    assert client.get("/events", params=params).status_code == 422


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


def test_incident_report_without_ai(client, monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "off")
    report = client.get("/incident-report/192.168.1.99").json()

    assert report["source"] == "rules"
    assert report["risk_level"] == "HIGH"
    assert report["mitre_technique"] == "T1078"


def test_incident_report_unknown_ip(client):
    response = client.get("/incident-report/10.0.0.1")
    assert response.status_code == 404
