# ML Service Observability Lab

This workspace contains a minimal FastAPI inference service instrumented with Prometheus metrics, JSON structured logs, and a local Docker Compose stack for Prometheus and Grafana.

## Files

- `app.py`: inference service with `/predict`, `/health`, and `/metrics`
- `requirements.txt`: Python dependencies
- `docker-compose.yml`: Prometheus and Grafana stack
- `prometheus.yml`: Prometheus scrape configuration

## 1. Start the inference service

Create a virtual environment if you want one, then install dependencies:

```bash
pip install -r requirements.txt
uvicorn app:app --host 0.0.0.0 --port 8000
```

Test the service:

```bash
curl http://localhost:8000/health

curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"features":[1,2,3]}'
```

Check raw Prometheus output:

```bash
curl http://localhost:8000/metrics
```

## 2. Start Prometheus and Grafana

Run the monitoring stack:

```bash
docker compose up -d
```

Open:

- Prometheus: <http://localhost:9090>
- Grafana: <http://localhost:3000>

Grafana defaults:

- Username: `admin`
- Password: `admin`

Add a Prometheus data source in Grafana with URL `http://prometheus:9090`.

## 3. Generate traffic

Send multiple requests to create logs and metrics:

```bash
for i in {1..20}; do
  curl -s -X POST http://localhost:8000/predict \
    -H "Content-Type: application/json" \
    -d '{"features":[1,2,3]}' > /dev/null
done
```

The service logs JSON lines similar to:

```json
{"timestamp":"2026-03-16 11:30:00,000","level":"INFO","logger":"ml-service","message":"prediction_made","event":"prediction_made","path":"/predict","client":"127.0.0.1","model_version":"1.0.0","features_count":3,"feature_mean":2.0,"prediction":"high_risk","drift_score":0.0}
```

## 4. Suggested Grafana panels

Use Prometheus queries such as:

- `sum(inference_requests_total) by (status)`
- `rate(inference_requests_total[1m])`
- `histogram_quantile(0.95, sum(rate(inference_request_latency_seconds_bucket[5m])) by (le))`
- `sum(inference_predictions_total) by (prediction)`
- `mock_feature_drift_score`

## 5. Logging and metric design

Structured logging fields included in this example:

- `event`
- `path`
- `client`
- `model_version`
- `features_count`
- `feature_mean`
- `prediction`
- `drift_score`

Metrics included in this example:

- Request count by method, endpoint, and status
- Request latency histogram for `/predict`
- Prediction count by label
- In-progress request gauge
- Mock feature drift gauge

## 6. Reflection prompts

- How would you add a request or correlation ID so logs can be tied to downstream systems?
- Which latency percentile is most useful for an inference API: p50, p95, or p99?
- In production, would drift and accuracy be computed inline, asynchronously, or in a separate monitoring job?
