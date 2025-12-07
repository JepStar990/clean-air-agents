"""
FastAPI gateway: health, OpenAQ fetch (v3), analysis (single pass), A2A.
Observability hooks initialized here.

OpenAQ v3 docs (API key + endpoints):
- API Docs & examples: https://docs.openaq.org/                         [2](https://linuxtldr.com/setup-ollama-and-open-webui-on-linux/)
- Latest resource examples: https://docs.openaq.org/resources/latest      [4](https://signoz.io/blog/opentelemetry-fastapi/)
- Parameters (PM2.5 is id=2): https://docs.openaq.org/resources/parameters/2  [3](https://www.tech2geek.net/how-to-run-local-llms-on-linux-with-ollama-and-lm-studio/)
"""

from fastapi import FastAPI, Query
from app.settings import settings
from fastapi.staticfiles import StaticFiles

# Observability
from app.observability_init import init_observability

# OpenAQ v3 client (Johannesburg-first PM2.5 latest)
from app.tools.openaq_api import fetch_latest_pm25

# Analytics pipeline (uses v3 client internally)
from app.analytics.endpoints import analyze_pm25_pipeline

# A2A minimal endpoints
from app.a2a.server import router as a2a_router


app = FastAPI(title="CleanAir Agents (Johannesburg-first)")

# Initialize OpenTelemetry traces + Prometheus metrics
init_observability(app, enable_metrics=settings.PROMETHEUS_ENABLED)


# Serve static React build (copied to app/static by Dockerfile)
app.mount("/", StaticFiles(directory="app/static", html=True), name="static")

# Expose A2A routes
app.include_router(a2a_router, prefix="/a2a")


@app.get("/health")
def health():
    return {"ok": True}


@app.get("/api/openaq")
async def openaq(
    city: str = Query(settings.DEFAULT_CITY),
    country: str = Query(settings.DEFAULT_COUNTRY),
    limit: int = Query(50, ge=1, le=1000),
):
    """
    Fetch latest PM2.5 for the given city & country using OpenAQ v3.
    Requires X-API-Key (OPENAQ_API_KEY env).

    Example:
      GET /api/openaq?city=Johannesburg&country=ZA&limit=50
    """
    data = await fetch_latest_pm25(country_iso=country, city=city, limit=limit)
    return data


@app.get("/api/analyze")
async def analyze(
    city: str = Query(settings.DEFAULT_CITY),
    country: str = Query(settings.DEFAULT_COUNTRY),
    model: str = Query("llama3.1:latest"),
):
    """
    End-to-end pipeline:
      1) Fetch latest PM2.5 via OpenAQ v3
      2) Compute exceedances & hotspots
      3) Draft concise policy via Ollama

    Example:
      GET /api/analyze?city=Johannesburg&country=ZA&model=llama3.1:latest
    """
    result = await analyze_pm25_pipeline(city=city, country=country, model=model)
    return result
