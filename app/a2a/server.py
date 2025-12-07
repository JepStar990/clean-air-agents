"""
Minimal A2A endpoints (message/send, message/stream stub, tasks/get).
This is a simplified implementation for interop testing.

A2A documentation & LangGraph A2A support references: [5](https://www.guiahardware.es/en/Hardware-requirements-for-using-Ollama-with-local-models/) [6](https://github.com/a2aproject/A2A)
"""

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
import json
from pathlib import Path
from app.analytics.endpoints import analyze_pm25_pipeline

router = APIRouter()


@router.get("/.well-known/agent-card.json")
async def agent_card():
    card = json.loads(Path(__file__).with_name("agent_card.json").read_text())
    return JSONResponse(card)


@router.post("/message/send")
async def message_send(req: Request):
    """
    Expect body:
    {
      "input": {"city":"Johannesburg","country":"ZA","model":"llama3:8b-instruct-q4"}
    }
    """
    body = await req.json()
    inp = body.get("input", {})
    city = inp.get("city", "Johannesburg")
    country = inp.get("country", "ZA")
    model = inp.get("model", "llama3:8b-instruct-q4")
    result = await analyze_pm25_pipeline(city=city, country=country, model=model)
    return JSONResponse({"status": "complete", "result": result})


@router.post("/message/stream")
async def message_stream(req: Request):
    # Stub: convert to SSE/streaming if desired
    body = await req.json()
    return JSONResponse({"status": "not-implemented", "echo": body})


@router.get("/tasks/get")
async def tasks_get(task_id: str):
    # Stub: no task store yet
    return JSONResponse({"task_id": task_id, "status": "not-implemented"})
