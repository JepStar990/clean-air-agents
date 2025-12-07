"""
Analytics pipeline (OpenAQ v3):
- fetch_latest_pm25 (parameter id 2, PM2.5) with ISO and city filter.
- analyze_measurements (count, exceedances, top locations).
- draft_policy (Ollama).
"""

from typing import Dict, Any
from app.tools.openaq_api import fetch_latest_pm25
from app.agents.analytics_agent import analyze_measurements
from app.agents.policy_agent import draft_policy
from app.settings import settings


async def analyze_pm25_pipeline(city: str, country: str, model: str) -> Dict[str, Any]:
    # 1) Fetch latest PM2.5 for country/city (OpenAQ v3, requires API key). [2](https://linuxtldr.com/setup-ollama-and-open-webui-on-linux/)
    data = await fetch_latest_pm25(country_iso=country, city=city, limit=500)

    # 2) Analyze
    summary = analyze_measurements(data.get("results", []))

    # 3) Draft policy (short advisory)
    policy_text = await draft_policy(model=model, city=city, analytics_summary=summary)

    return {
        "city": city,
        "country": country,
        "analytics": summary,
        "policy": policy_text,
        "score": None,
        "source": {"openaq": settings.OPENAQ_API_BASE, "v": "v3"}
    }
