from ai.evidence import redact


def test_aws_key_id_is_redacted():
    text = "error using AKIAIOSFODNN7EXAMPLE in request"
    assert "AKIAIOSFODNN7EXAMPLE" not in redact(text)


def test_password_and_token_values_are_redacted():
    result = redact("DB_PASSWORD=hunter2 and api_key: sk-fake-123")
    assert "hunter2" not in result
    assert "sk-fake-123" not in result
    assert "DB_PASSWORD=" in result


def test_bearer_token_is_redacted():
    result = redact("Authorization: Bearer abc.def-123")
    assert "abc.def-123" not in result


def test_private_key_block_is_redacted():
    text = "-----BEGIN RSA PRIVATE KEY-----\nMIIEfakekeydata\n-----END RSA PRIVATE KEY-----"
    assert "MIIEfakekeydata" not in redact(text)


def test_normal_log_text_is_unchanged():
    text = "container exited with code 1 at 10:03"
    assert redact(text) == text
