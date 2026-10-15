import re

# Each rule: pattern to find, text to put in its place
PATTERNS = [
    # AWS access key IDs
    (re.compile(r"AKIA[0-9A-Z]{16}"), "[REDACTED_AWS_KEY_ID]"),
    # Whole private key blocks
    (
        re.compile(
            r"-----BEGIN [A-Z ]*PRIVATE KEY-----.*?-----END [A-Z ]*PRIVATE KEY-----",
            re.DOTALL,
        ),
        "[REDACTED_PRIVATE_KEY]",
    ),
    # password=..., token: ..., api_key=..., aws_secret_access_key=...
    (
        re.compile(
            r"(?i)(password|passwd|secret|token|api[_-]?key|aws_secret_access_key)"
            r"(\s*[=:]\s*)(\S+)"
        ),
        r"\1\2[REDACTED]",
    ),
    # Authorization: Bearer <token>
    (re.compile(r"(?i)bearer\s+[A-Za-z0-9._\-]+"), "Bearer [REDACTED]"),
]


def redact(text):
    """Remove secrets from text before it is stored or sent to an LLM."""
    for pattern, replacement in PATTERNS:
        text = pattern.sub(replacement, text)
    return text
