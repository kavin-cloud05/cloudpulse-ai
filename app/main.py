from flask import Flask, jsonify, request

from ai.diagnostics import diagnose
from app.services.health import run_health_check

MAX_EVIDENCE_CHARS = 5000


def create_app():
    app = Flask(__name__)

    @app.get("/health")
    def health():
        return jsonify(status="healthy", service="cloudpulse-api")

    @app.get("/api/v1/system")
    def system():
        return jsonify(run_health_check())

    @app.post("/api/v1/diagnose")
    def diagnose_route():
        data = request.get_json(silent=True)
        evidence = data.get("evidence") if isinstance(data, dict) else None
        if not isinstance(evidence, str) or not evidence.strip():
            return jsonify(error="'evidence' must be a non-empty string"), 400
        if len(evidence) > MAX_EVIDENCE_CHARS:
            return (
                jsonify(error=f"'evidence' must be at most {MAX_EVIDENCE_CHARS} characters"),
                400,
            )
        return jsonify(diagnose(evidence))

    return app


app = create_app()
