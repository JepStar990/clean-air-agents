"""
Policy evaluation: returns a JSON-like score (clarity, feasibility, impact, overall).
This can be used with a LangGraph loop to iterate until overall >= threshold.
"""

import re
import json
from app.ollama_client import OllamaClient


async def evaluate_policy(model: str, policy_text: str) -> dict:
    oc = OllamaClient()
    rubric = """
Score the following policy (0–1) on clarity, feasibility, and expected impact.
Return strict JSON:

{"clarity":float,"feasibility":float,"impact":float,"overall":float,"feedback":"..."}
"""
    raw = await oc.generate(model=model, prompt=rubric + "\n\n" + policy_text, temperature=0.0)
    try:
        j = json.loads(re.search(r"\{.*\}", raw, re.S).group(0))
        return j
    except Exception:
        return {"clarity": 0.0, "feasibility": 0.0, "impact": 0.0, "overall": 0.0, "feedback": "parse_error"}
