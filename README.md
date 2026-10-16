# CloudPulse AI

A small cloud-operations tool that checks a Linux server's health and explains common errors with step-by-step troubleshooting. It is read-only: it never runs commands for you.

Built on an AWS EC2 Ubuntu server with Bash, Python, Flask, pytest and Docker.

## What works today

- [x] Linux health check script (CPU, memory, disk, uptime, top processes) with warning and critical thresholds and exit codes 0, 1, 2
- [x] Flask API: GET /health, GET /api/v1/system, POST /api/v1/diagnose, GET /api/v1/incidents
- [x] Rule-based diagnostics for 6 common problems: disk full, port in use, connection refused, AWS AccessDenied, out of memory, permission denied
- [x] Secret redaction (AWS key IDs, passwords, tokens, private keys) before evidence is processed
- [x] Input validation on the diagnose endpoint (must be a non-empty string, max 5000 characters)
- [x] 24 automated pytest tests
- [x] Backend runs in a Docker container with gunicorn as a non-root user
- [x] MySQL incident history via Docker Compose: each diagnosis is saved and listed at GET /api/v1/incidents (data survives restarts)

## Not built yet

- [ ] LLM-generated explanations (the field exists in the response but is empty)
- [ ] React dashboard, chatbot
- [ ] Jenkins, ECR, Kubernetes, Ansible, Prometheus, Grafana

## Run it

    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    python -m pytest -q
    flask --app app.main run --port 5000

With Docker:

    docker build -f docker/Dockerfile.backend -t cloudpulse-backend .
    docker run -d --name cloudpulse-backend -p 5000:5000 cloudpulse-backend
    curl http://localhost:5000/health

Try a diagnosis:

    curl -X POST http://localhost:5000/api/v1/diagnose \
      -H "Content-Type: application/json" \
      -d '{"evidence": "write failed: No space left on device"}'

## Design rules

- Only the evidence text decides what is reported as confirmed. Possible causes are listed separately as things to check.
- Logs are treated as untrusted input. The health script is run with a fixed command and no user input reaches a shell.
- Secrets are never committed. .env and key files are in .gitignore and .dockerignore.

## Known limitations

- Inside a container, the health script reports the host's CPU and memory because containers share the host kernel. Disk shows the container's filesystem.
- Diagnostics are keyword rules, so they only recognise the patterns listed above.
- Runs on one development EC2 instance. It is not a production deployment.
