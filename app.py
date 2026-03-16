import json
import logging
import time
from typing import Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import Response
from prometheus_client import CONTENT_TYPE_LATEST
from prometheus_client import Counter
from prometheus_client import Gauge
from prometheus_client import Histogram
from prometheus_client import generate_latest
from pydantic import BaseModel, Field


MODEL_VERSION = "1.0.0"
TRAINING_FEATURE_MEAN = 2.0


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        extra_fields = {
            key: value
            for key, value in record.__dict__.items()
            if key
            not in {
                "args",
                "created",
                "exc_info",
                "exc_text",
                "filename",
                "funcName",
                "levelname",
                "levelno",
                "lineno",
                "module",
                "msecs",
                "message",
                "msg",
                "name",
                "pathname",
                "process",
                "processName",
                "relativeCreated",
                "stack_info",
                "thread",
                "threadName",
            }
        }
        payload.update(extra_fields)
        return json.dumps(payload, default=str)


def configure_logger() -> logging.Logger:
    logger = logging.getLogger("ml-service")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()

    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter())
    logger.addHandler(handler)
    logger.propagate = False
    return logger


logger = configure_logger()


REQUEST_COUNT = Counter(
    "inference_requests_total",
    "Total number of prediction requests",
    ["method", "endpoint", "status"],
)
REQUEST_LATENCY = Histogram(
    "inference_request_latency_seconds",
    "Latency of prediction requests",
    ["endpoint"],
    buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0),
)
PREDICTION_COUNT = Counter(
    "inference_predictions_total",
    "Total predictions by output class",
    ["prediction"],
)
IN_PROGRESS = Gauge(
    "inference_requests_in_progress",
    "Number of in-flight prediction requests",
)
FEATURE_DRIFT = Gauge(
    "mock_feature_drift_score",
    "Absolute difference between current request mean and training mean",
)


class PredictRequest(BaseModel):
    features: list[float] = Field(..., min_length=1, description="Numeric feature vector")


class PredictResponse(BaseModel):
    prediction: str
    model_version: str
    drift_score: float


def predict(features: list[float]) -> str:
    score = sum(features) / len(features)
    return "high_risk" if score >= TRAINING_FEATURE_MEAN else "low_risk"


def compute_drift(features: list[float]) -> float:
    current_mean = sum(features) / len(features)
    return abs(current_mean - TRAINING_FEATURE_MEAN)


app = FastAPI(title="ML Inference Observability Lab", version=MODEL_VERSION)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "model_version": MODEL_VERSION}


@app.post("/predict", response_model=PredictResponse)
async def predict_endpoint(payload: PredictRequest, request: Request) -> PredictResponse:
    if not payload.features:
        raise HTTPException(status_code=400, detail="features must not be empty")

    start = time.perf_counter()
    IN_PROGRESS.inc()
    status = "success"

    try:
        prediction = predict(payload.features)
        drift_score = compute_drift(payload.features)
        FEATURE_DRIFT.set(drift_score)
        PREDICTION_COUNT.labels(prediction=prediction).inc()

        logger.info(
            "prediction_made",
            extra={
                "event": "prediction_made",
                "path": request.url.path,
                "client": request.client.host if request.client else "unknown",
                "model_version": MODEL_VERSION,
                "features_count": len(payload.features),
                "feature_mean": round(sum(payload.features) / len(payload.features), 4),
                "prediction": prediction,
                "drift_score": round(drift_score, 4),
            },
        )

        return PredictResponse(
            prediction=prediction,
            model_version=MODEL_VERSION,
            drift_score=round(drift_score, 4),
        )
    except Exception:
        status = "error"
        logger.exception(
            "prediction_failed",
            extra={"event": "prediction_failed", "path": request.url.path},
        )
        raise
    finally:
        elapsed = time.perf_counter() - start
        REQUEST_COUNT.labels(
            method=request.method,
            endpoint=request.url.path,
            status=status,
        ).inc()
        REQUEST_LATENCY.labels(endpoint=request.url.path).observe(elapsed)
        IN_PROGRESS.dec()


@app.get("/metrics")
def metrics() -> Response:
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.get("/")
def root() -> dict[str, Any]:
    return {
        "service": "ml-inference-observability-lab",
        "model_version": MODEL_VERSION,
        "endpoints": ["/health", "/predict", "/metrics"],
    }
