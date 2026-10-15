from app.main import create_app


def client():
    return create_app().test_client()


def test_health_returns_healthy():
    response = client().get("/health")
    assert response.status_code == 200
    assert response.get_json() == {"status": "healthy", "service": "cloudpulse-api"}


def test_system_returns_expected_fields():
    response = client().get("/api/v1/system")
    assert response.status_code == 200
    data = response.get_json()
    assert data["overall"] in ("ok", "warning", "critical")
    assert set(data["metrics"]) == {"cpu", "memory", "disk"}


def test_unknown_route_returns_404():
    assert client().get("/does-not-exist").status_code == 404


def test_wrong_method_returns_405():
    assert client().post("/health").status_code == 405
