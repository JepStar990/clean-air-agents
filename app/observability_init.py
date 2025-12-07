"""
Initialize observability:
- OpenTelemetry FastAPI instrumentation for traces
- Prometheus metrics (via prometheus_fastapi_instrumentator)

OpenTelemetry FastAPI instrumentation reference: [3](https://www.bitdoze.com/mcp-introduction-beginners/)
Grafana FastAPI dashboard reference: [4](https://launchspace.net/product/fly-io-pricing-overview/)
"""

import os
from fastapi import FastAPI
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from prometheus_fastapi_instrumentator import Instrumentator


def init_observability(app: FastAPI, enable_metrics: bool = True) -> None:
    """
    Call once from app startup.
    To export traces to an OTLP collector, set env vars, e.g.:
      OTEL_EXPORTER_OTLP_ENDPOINT=http://otel-collector:4318
      OTEL_SERVICE_NAME=clean-air-agents
      OTEL_RESOURCE_ATTRIBUTES=deployment.environment=dev
    """
    # Tracing
    FastAPIInstrumentor.instrument_app(app)

    # Metrics
    if enable_metrics:
        Instrumentator().instrument(app).expose(app)

    # Simple log of what's enabled
    app.logger if hasattr(app, "logger") else None
