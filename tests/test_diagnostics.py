from ai.diagnostics import diagnose


def test_disk_full_is_detected():
    report = diagnose("write failed: No space left on device")
    assert report["matched"] is True
    assert report["findings"][0]["rule"] == "disk_full"


def test_unknown_error_has_no_findings():
    report = diagnose("everything looks fine today")
    assert report["matched"] is False
    assert report["findings"] == []


def test_secrets_are_redacted_in_report():
    report = diagnose("password=hunter2 connection refused")
    assert "hunter2" not in report["evidence"]


def test_multiple_problems_are_both_reported():
    report = diagnose("Permission denied, then: Address already in use")
    rules = {finding["rule"] for finding in report["findings"]}
    assert {"permission_denied", "port_in_use"} <= rules
