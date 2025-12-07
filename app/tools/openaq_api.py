"""
OpenAQ v3 client (Johannesburg-first PM2.5 latest).
Docs & examples (v3, API key header X-API-Key): [2](https://linuxtldr.com/setup-ollama-and-open-webui-on-linux/)
PM2.5 parameter id = 2: [3](https://www.tech2geek.net/how-to-run-local-llms-on-linux-with-ollama-and-lm-studio/)
Locations & latest resources: [4](https://uptrace.dev/guides/opentelemetry-fastapi)[5](https://signoz.io/blog/opentelemetry-fastapi/)
"""

from typing import Optional, List, Dict
import httpx
from app.settings import settings


PARAM_PM25_ID = 2  # documented id for PM2.5 [3](https://www.tech2geek.net/how-to-run-local-llms-on-linux-with-ollama-and-lm-studio/)


def _headers():
    # v3 requires X-API-Key (401 Unauthorized without it). [2](https://linuxtldr.com/setup-ollama-and-open-webui-on-linux/)
    h = {}
    if settings.OPENAQ_API_KEY:
        h["X-API-Key"] = settings.OPENAQ_API_KEY
    return h


async def fetch_latest_pm25(country_iso: str, city: Optional[str] = None, limit: int = 1000) -> Dict:
    """
    Strategy:
      - Call /v3/parameters/2/latest?iso=ZA to get latest PM2.5 readings.
      - Lookup location names via /v3/locations/{id}, then filter to city if provided.
      - Return a simplified structure compatible with analytics.

    NOTE: This favors freshness and speed. For time-series, use sensors/{id}/hours/days/measurements. [6](https://dev.sh20raj.com/ken_mwaura1/getting-started-monitoring-a-fastapi-app-with-grafana-and-prometheus-a-step-by-step-guide-3fbn)
    """
    base = settings.OPENAQ_API_BASE.rstrip("/")
    url = f"{base}/parameters/{PARAM_PM25_ID}/latest"
    params = {"iso": country_iso, "limit": limit}

    async with httpx.AsyncClient(timeout=60) as client:
        r = await client.get(url, params=params, headers=_headers())
        r.raise_for_status()
        payload = r.json()  # { meta, results: [ { value, datetime, coordinates, sensorsId, locationsId } ... ] }

        results = payload.get("results", [])
        simplified: List[Dict] = []

        for row in results:
            val = row.get("value")
            loc_id = row.get("locationsId")
            locality_name = None

            if loc_id is not None:
                loc_url = f"{base}/locations/{loc_id}"  # location details include "locality" [7](https://www.byteplus.com/en/topic/456662?title=list-all-models-in-ollama-complete-guide-for-2025)
                lr = await client.get(loc_url, headers=_headers())
                if lr.status_code == 200:
                    loc_payload = lr.json()
                    loc_items = loc_payload.get("results", [])
                    if loc_items:
                        locality_name = loc_items[0].get("locality")

            # City filter (Johannesburg-first)
            if city and locality_name and locality_name.lower() != city.lower():
                continue

            simplified.append({
                "value": val,
                "location": locality_name or str(loc_id),
                "raw": row
            })

        return {"results": simplified}
