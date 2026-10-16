from app.main import create_app


def client():
    return create_app().test_client()


def test_incidents_returns_503_without_database(monkeypatch):
    monkeypatch.delenv("MYSQL_HOST", raising=False)
    assert client().get("/api/v1/incidents").status_code == 503


def test_diagnose_works_without_database(monkeypatch):
    monkeypatch.delenv("MYSQL_HOST", raising=False)
    response = client().post(
        "/api/v1/diagnose", json={"evidence": "No space left on device"}
    )
    assert response.status_code == 200
    assert response.get_json()["incident_id"] is None


def test_diagnose_returns_saved_incident_id(monkeypatch):
    monkeypatch.setattr("app.main.save_incident", lambda report: 42)
    response = client().post(
        "/api/v1/diagnose", json={"evidence": "No space left on device"}
    )
    assert response.get_json()["incident_id"] == 42


def test_incidents_lists_rows_from_database(monkeypatch):
    monkeypatch.setattr("app.main.db_enabled", lambda: True)
    monkeypatch.setattr(
        "app.main.list_incidents",
        lambda: [{"id": 1, "status": "open", "rules": "disk_full"}],
    )
    response = client().get("/api/v1/incidents")
    assert response.status_code == 200
    assert response.get_json()["incidents"][0]["rules"] == "disk_full"
