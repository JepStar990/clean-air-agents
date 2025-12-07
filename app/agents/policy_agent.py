"""
Policy drafting: LLM writes a concise advisory tailored to the city.
"""

from app.ollama_client import OllamaClient


async def draft_policy(model: str, city: str, analytics_summary: dict) -> str:
    oc = OllamaClient()
    prompt = f"""
You are a public health policy advisor for {city}.
Data summary: {analytics_summary}
Write a concise advisory for municipal stakeholders:
- 3 actions for transport emissions
- 3 for indoor air
- 3 for community alerts
Include quick wins and medium-term actions. Use bullet points.
"""
    return await oc.generate(model=model, prompt=prompt, temperature=0.2)
