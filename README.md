# AskLaw — Monitoring Setup

This repository now includes Prometheus and Grafana integration for monitoring the backend.

Quick start with Docker Compose:

```powershell
# from repository root (Windows PowerShell)
docker-compose up --build -d

# open Prometheus UI at http://localhost:9090
# open Grafana UI at http://localhost:3000 (default login: admin/admin)
```

What was added:
- `prometheus/prometheus.yml` — Prometheus scrape configuration (scrapes `backend:8000/metrics`).
- `grafana/provisioning/datasources/datasource.yml` — auto-configures Prometheus as Grafana datasource.
- `backend/requirements.txt` — added `prometheus_client`.
- `backend/app/main.py` — mounts `/metrics` and records request counters and latency.
- `docker-compose.yml` — added `prometheus` and `grafana` services.

Notes:
- Grafana will prompt for initial credentials on first run (default `admin:admin`). Change the password.
- You can add dashboards in Grafana or import Prometheus-based dashboards for FastAPI/Starlette.
