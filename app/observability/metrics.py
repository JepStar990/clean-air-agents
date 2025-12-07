from prometheus_fastapi_instrumentator import Instrumentator

def init_metrics(app):
    # Exposes /metrics for Prometheus scraping
    Instrumentator().instrument(app).expose(app)  # [6](https://askai.glarity.app/search/Is-Fly-io-free-to-use)

