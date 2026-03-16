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
