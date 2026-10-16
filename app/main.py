import pymysql
from flask import Flask, jsonify, request

from ai.diagnostics import diagnose
from app.services.db import db_enabled, list_incidents, save_incident
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
        report = diagnose(evidence)
        report["incident_id"] = save_incident(report) if report["matched"] else None
        return jsonify(report)

    @app.get("/api/v1/incidents")
    def incidents():
        if not db_enabled():
            return jsonify(error="database is not configured"), 503
        try:
            return jsonify(incidents=list_incidents())
        except pymysql.MySQLError:
            return jsonify(error="database is unavailable"), 503

    return app


app = create_app()
