# ML Service Observability Lab Report

## Deliverables

- Inference service code with logging and Prometheus instrumentation: `app.py`
- Monitoring stack configuration: `docker-compose.yml` and `prometheus.yml`
- Grafana dashboard screenshot showing live metrics
- Short description of the logging approach and reflection on the setup

## Overview

This lab implements a minimal FastAPI-based inference service that exposes a `/predict` endpoint for model predictions, a `/health` endpoint for service checks, and a `/metrics` endpoint for Prometheus scraping. The service includes Prometheus metrics for request count, request rate, latency, prediction totals, and a mock ML-specific drift score. Grafana is used to visualize these metrics in a dashboard.

## Logging Approach

The inference service uses structured JSON logging so each prediction request generates a machine-readable log entry. The log records include fields such as `event`, `path`, `client`, `model_version`, `features_count`, `feature_mean`, `prediction`, and `drift_score`. These fields make it easier to debug request behavior, inspect model outputs, and trace service activity compared with unstructured console logging.

## Metrics Implemented

- `inference_requests_total`: total requests grouped by method, endpoint, and status
- `inference_request_latency_seconds`: latency histogram for the prediction endpoint
- `inference_predictions_total`: total predictions grouped by output label
- `inference_requests_in_progress`: gauge for in-flight prediction requests
- `mock_feature_drift_score`: gauge representing a simple feature drift signal

## Dashboard Summary

The Grafana dashboard includes four panels:

- Request Count
- Request Rate
- Predictions by Label
- Drift Score

These panels provide a basic observability view of the service by showing traffic volume, current request throughput, prediction outputs, and an ML-specific monitoring metric.

## Reflection

For this lab, I defined metrics around service activity and model behavior so that both system-level and ML-level signals could be observed in one place. Prometheus scraped the FastAPI application’s `/metrics` endpoint, and Grafana visualized the collected data in a dashboard. The dashboard showed successful requests, request rate, prediction totals, and a mock drift metric, which together provided a practical example of observability for an ML inference service.

One challenge in this lab was configuring the local monitoring setup and ensuring Prometheus and Grafana connected correctly to the running application. After the services were started, the metrics appeared as expected and could be queried and visualized without issue. In a production scenario, I would extend this setup by adding correlation IDs to logs, focusing on p95 or p99 latency for performance monitoring, and computing drift or accuracy in a separate monitoring pipeline rather than only within the request path.

## Reflection Prompts

### How would you add a request or correlation ID so logs can be tied to downstream systems?

I would capture a request ID from an incoming header such as `X-Request-ID`, or generate one at the start of the request if it is missing. That ID would then be included in every structured log entry and forwarded to downstream services through request headers. This would make it possible to trace a single request across the full system and simplify debugging when multiple components are involved.

### Which latency percentile is most useful for an inference API: p50, p95, or p99?

For an inference API, p95 is usually the most useful latency percentile because it highlights slow requests without being as unstable as p99. P50 shows the typical response time, but it can hide outliers that affect user experience. P99 is still valuable for deeper production monitoring, but p95 is often the best main signal for tracking service responsiveness.

### In production, would drift and accuracy be computed inline, asynchronously, or in a separate monitoring job?

In production, I would avoid computing full drift and accuracy inline during every prediction because that can increase latency and add unnecessary work to the serving path. Instead, I would capture lightweight request information during inference and perform detailed drift and accuracy calculations asynchronously or in a separate monitoring job. This approach is more scalable, keeps inference fast, and better matches real systems where ground truth often arrives later.
