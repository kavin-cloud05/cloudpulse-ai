from app.main import create_app


def post(body):
    return create_app().test_client().post("/api/v1/diagnose", json=body)


def test_valid_evidence_returns_findings():
    response = post({"evidence": "write failed: No space left on device"})
    assert response.status_code == 200
    assert response.get_json()["matched"] is True


def test_missing_evidence_returns_400():
    assert post({}).status_code == 400


def test_non_string_evidence_returns_400():
    assert post({"evidence": 123}).status_code == 400


def test_too_long_evidence_returns_400():
    assert post({"evidence": "x" * 5001}).status_code == 400
