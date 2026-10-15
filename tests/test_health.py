from types import SimpleNamespace

from app.services import health

FAKE_OUTPUT = (
    "CPU:     95%  [CRITICAL]\n"
    "Memory:  50%  [OK]\n"
    "Disk /:  80%  [WARNING]\n"
)


def fake_run(exit_code):
    def _run(*args, **kwargs):
        return SimpleNamespace(stdout=FAKE_OUTPUT, returncode=exit_code)
    return _run


def test_critical_exit_code_maps_to_critical(monkeypatch):
    monkeypatch.setattr(health.subprocess, "run", fake_run(2))
    result = health.run_health_check()
    assert result["overall"] == "critical"
    assert result["metrics"]["cpu"] == {"percent": 95, "level": "critical"}
    assert result["metrics"]["disk"]["level"] == "warning"


def test_warning_exit_code_maps_to_warning(monkeypatch):
    monkeypatch.setattr(health.subprocess, "run", fake_run(1))
    assert health.run_health_check()["overall"] == "warning"


def test_unknown_exit_code_maps_to_unknown(monkeypatch):
    monkeypatch.setattr(health.subprocess, "run", fake_run(7))
    assert health.run_health_check()["overall"] == "unknown"
