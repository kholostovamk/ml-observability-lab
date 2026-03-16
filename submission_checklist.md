# Submission Checklist


- `app.py`
- `docker-compose.yml`
- `prometheus.yml`
- `README.md`
- `report.md`
- One Grafana dashboard screenshot showing the panels

## Dashboard should show

- Request Count
- Request Rate
- Predictions by Label
- Drift Score

## Quick verification

- The FastAPI service responds at `http://localhost:8000/health`
- The prediction endpoint responds at `http://localhost:8000/predict`
- Prometheus opens at `http://localhost:9090`
- Grafana opens at `http://localhost:3000`
- Prometheus query `inference_requests_total` returns data

## Suggested submission package

- Source files from this folder
- Dashboard screenshot
- Written reflection from `report.md`
