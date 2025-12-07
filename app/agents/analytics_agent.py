"""
Basic analytics: count, exceedances vs WHO 24h guideline, and top locations.

This is intentionally simple to keep CPU costs low on small VMs.
"""

import pandas as pd
from typing import List, Dict

WHO_PM25_24H = 15  # μg/m³ threshold (illustrative)


def analyze_measurements(measurements: List[Dict] | Dict) -> Dict:
    # Accept OpenAQ {results: [...] } or a bare list of rows
    results = measurements if isinstance(measurements, list) else measurements.get("results", [])
    df = pd.DataFrame(results)
    if df.empty:
        return {"summary": "No data", "exceedances": 0, "count": 0, "top_locations": []}

    # Normalize columns
    if "value" not in df.columns:
        # Some bulk CSVs use 'value' but ensure numeric
        pass
    df["value"] = pd.to_numeric(df["value"], errors="coerce")

    # Basic stats
    exceed = int((df["value"] > WHO_PM25_24H).sum())
    count = int(len(df))
    # Top locations by last value
    cols = [c for c in ["location", "value"] if c in df.columns]
    top = df.nlargest(5, "value")[cols].to_dict(orient="records") if "value" in df.columns else []

    return {"count": count, "exceedances": exceed, "top_locations": top}
