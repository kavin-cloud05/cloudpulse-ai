from flask import Flask, jsonify

from app.services.health import run_health_check


def create_app():
    app = Flask(__name__)

    @app.get("/health")
    def health():
        return jsonify(status="healthy", service="cloudpulse-api")

    @app.get("/api/v1/system")
    def system():
        return jsonify(run_health_check())

    return app


app = create_app()
