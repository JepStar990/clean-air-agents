from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

def init_otel(app):
    # Configure exporter via OTEL_* env vars if using an OTLP collector
    FastAPIInstrumentor.instrument_app(app)  # FastAPI tracing instrumentation [5](https://www.bitdoze.com/mcp-introduction-beginners/)

