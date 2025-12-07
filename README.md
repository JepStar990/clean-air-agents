<<<<<<< HEAD
# CleanAir Agents (Johannesburg-first, globally-ready)
=======
# CleanAir Agents — Johannesburg-first, globally-ready
>>>>>>> fed6c59 (agent mvp1 working locally)

A multi-agent FastAPI application that pulls **OpenAQ** air-quality data (API + bulk), analyzes local PM2.5 trends for Johannesburg (or any city), and drafts short policy advisories using a local LLM via **Ollama**. Observability hooks (OpenTelemetry + Prometheus) are included.

## Why OpenAQ?
OpenAQ aggregates global air-quality measurements and exposes them via an open API and a daily S3 CSV archive—ideal for sustainability analysis and repeatable UAT.  
- API & registry details: https://registry.opendata.aws/openaq/ (S3 archive, hourly updates) [3](https://huggingface.co/docs/hub/spaces)  
- Platform overview & mission: https://openaq.org/ [4](https://huggingface.co/docs/hub/advanced-compute-options)

<<<<<<< HEAD
## Stack
- Python 3.11, FastAPI
- LangGraph (stateful multi-agent orchestration; loops, interrupts, checkpointing) [16](https://www.langchain.com/langgraph) [17](https://bix-tech.com/langgraph-in-practice-orchestrating-multiagent-systems-and-distributed-ai-flows-at-scale/)
- MCP/OpenAPI tools (OpenAQ API) [18](https://github.com/modelcontextprotocol) [19](https://modelcontextprotocol.io/docs/getting-started/intro)
- A2A Protocol stubs (agent card + endpoints) [20](https://a2a-protocol.org/dev/) [21](https://github.com/a2aproject/A2A)
- Observability: OpenTelemetry (FastAPI), Prometheus, Grafana dashboard (FastAPI references exist) [22](https://opentelemetry-python-contrib.readthedocs.io/en/latest/instrumentation/fastapi/fastapi.html) [23](https://grafana.com/grafana/dashboards/16110-fastapi-observability/)
- LLM runtime: **Ollama** (Llama 3/3.1 8B, Mistral 7B, Gemma, Qwen), minimum 8 GB RAM for 7B models, 16 GB recommended. [2](https://ollama.com/library/llama2:7b) [1](https://deepwiki.com/ollama/ollama/1.2-system-requirements)

## Quick start (on your Linux VM)
1. Install Ollama:
   ```bash
   curl -fsSL https://ollama.com/install.sh | sh && ollama pull llama3:8b && ollama serve

(7–8B quantized models fit into 8 GB RAM; performance improves with 16 GB.) [\[deepwiki.com\]](https://deepwiki.com/ollama/ollama/1.2-system-requirements), [\[isitdev.com\]](https://isitdev.com/run-llms-locally-ollama-llama-3-2025/)

2.  Python env:
    ```bash
    python -m venv .venv && source .venv/bin/activate
    pip install -r requirements.txt
    ```

3.  Run backend:
    ```bash
    uvicorn app.main:app --host 0.0.0.0 --port 8000
    ```

4.  Run React client:
    ```bash
    cd client
    npm i
    npm run dev
    ```

5.  Observability (optional; local only):
    ```bash
    docker compose -f infra/docker-compose.yml up -d
    # Grafana at http://localhost:3000 (admin/admin)
    ```

## Deployments (free)

*   **Render Free Web Service** (simple, cold-start after 15 min idle) [\[render.com\]](https://render.com/docs/free)
*   **Cloud Run Free tier** (always-free quotas like vCPU-seconds, 1 GiB egress NA) [\[cloud.google.com\]](https://cloud.google.com/run/pricing), [\[freetiers.com\]](https://www.freetiers.com/directory/google-cloud-run)
*   **Hugging Face Spaces** for client demos; CPU is free, ZeroGPU for occasional GPU demos [\[huggingface.co\]](https://huggingface.co/docs/hub/spaces), [\[huggingface.co\]](https://huggingface.co/docs/hub/spaces-zerogpu)

## Switch to global

Use `scope=global` query param in client or set `GLOBAL_DEFAULT=true` in `.env`. Backend routes accept `country`, `city`, or default to **Johannesburg**.



### 2.2 `requirements.txt`
```txt
fastapi==0.115.5
uvicorn[standard]==0.30.1
httpx==0.27.2
pydantic==2.9.1
langgraph==0.2.30
prometheus-client==0.20.0
prometheus-fastapi-instrumentator==6.1.0
opentelemetry-api==1.26.0
opentelemetry-sdk==1.26.0
opentelemetry-instrumentation-fastapi==0.46b0
opentelemetry-exporter-otlp==1.26.0
pandas==2.2.3
matplotlib==3.9.2
python-dotenv==1.0.1
````

*(OpenTelemetry FastAPI instrumentation exists and is current; Prometheus + Grafana references are widely used with FastAPI.)* [\[openteleme...thedocs.io\]](https://opentelemetry-python-contrib.readthedocs.io/en/latest/instrumentation/fastapi/fastapi.html), [\[dev.to\]](https://dev.to/ken_mwaura1/getting-started-monitoring-a-fastapi-app-with-grafana-and-prometheus-a-step-by-step-guide-3fbn), [\[grafana.com\]](https://grafana.com/grafana/dashboards/16110-fastapi-observability/)

***

### 2.3 Backend

#### `app/settings.py`

```python
from pydantic import BaseSettings

class Settings(BaseSettings):
    OLLAMA_HOST: str = "http://localhost:11434"
    DEFAULT_CITY: str = "Johannesburg"
    DEFAULT_COUNTRY: str = "ZA"
    GLOBAL_DEFAULT: bool = False
    PROMETHEUS_ENABLED: bool = True

settings = Settings()
```

#### `app/ollama_client.py`

```python
import httpx
from app.settings import settings

class OllamaClient:
    def __init__(self, host: str = settings.OLLAMA_HOST):
        self.host = host.rstrip("/")

    async def generate(self, model: str, prompt: str, temperature: float = 0.2):
        url = f"{self.host}/api/generate"
        payload = {"model": model, "prompt": prompt, "stream": False, "options": {"temperature": temperature}}
        async with httpx.AsyncClient(timeout=60) as client:
            r = await client.post(url, json=payload)
            r.raise_for_status()
            data = r.json()
            return data.get("response", "")
```

> Ollama exposes a local REST API on `:11434`. Use quantized 7–8B models (e.g., `llama3:8b-instruct-q4`). 7B models generally need ≥8 GB RAM; quantization reduces memory. [\[ollama.com\]](https://ollama.com/library/llama2:7b), [\[isitdev.com\]](https://isitdev.com/run-llms-locally-ollama-llama-3-2025/)

#### `app/tools/openaq_api.py` (API tool via HTTP)

```python
import httpx
from typing import Optional

OPENAQ_API = "https://api.openaq.org/v2/measurements"  # official endpoint [15](https://registry.opendata.aws/openaq/)

async def fetch_measurements(country: Optional[str]=None, city: Optional[str]=None, parameter: str="pm25", limit: int=200):
    params = {"parameter": parameter, "limit": limit}
    if country: params["country"] = country
    if city: params["city"] = city
    async with httpx.AsyncClient(timeout=60) as client:
        r = await client.get(OPENAQ_API, params=params)
        r.raise_for_status()
        return r.json()
```

#### `app/tools/bulk_ingest.py` (bulk CSV from S3)

```python
import os, gzip, csv
import httpx
from typing import List, Dict

# OpenAQ daily gzipped CSVs in AWS S3 registry (public, unsigned) [15](https://registry.opendata.aws/openaq/)
S3_BUCKET = "https://openaq-data-archive.s3.amazonaws.com/"

async def list_archive(prefix: str = "") -> List[str]:
    # Simplified: you can hardcode recent files or implement S3 listing via AWS CLI with --no-sign-request.
    # For demo, return a small fixed subset.
    return [f"{S3_BUCKET}2025-11-01.csv.gz", f"{S3_BUCKET}2025-11-02.csv.gz"]

async def download_csv_gz(url: str) -> List[Dict]:
    async with httpx.AsyncClient(timeout=120) as client:
        r = await client.get(url)
        r.raise_for_status()
        content = gzip.decompress(r.content).decode("utf-8", errors="replace")
        rows = []
        reader = csv.DictReader(content.splitlines())
        for row in reader:
            rows.append(row)
        return rows
```

#### `app/memory/session_store.py`

```python
from typing import Dict, Any

# Minimal in-memory session; replace with SQLite/Postgres in production
SESSIONS: Dict[str, Dict[str, Any]] = {}

def get_session(user_id: str) -> Dict[str, Any]:
    return SESSIONS.setdefault(user_id, {"history": [], "preferences": {}})
```

#### `app/memory/context_compaction.py`

```python
def compact_context(history, max_items=10):
    # naive compaction: last N + key facts
    return history[-max_items:]
```

#### `app/agents/analytics_agent.py`

```python
import pandas as pd
from typing import List, Dict

WHO_PM25_24H = 15  # μg/m³

def analyze_measurements(measurements: List[Dict]):
    # expect OpenAQ API response: {results: [{value, parameter, date: {utc}, location, ...}]}
    results = measurements if isinstance(measurements, list) else measurements.get("results", [])
    df = pd.DataFrame(results)
    if df.empty:
        return {"summary": "No data", "exceedances": 0}

    df["value"] = pd.to_numeric(df["value"], errors="coerce")
    exceed = (df["value"] > WHO_PM25_24H).sum()
    top = df.nlargest(5, "value")[["location", "value"]].to_dict(orient="records")
    return {"count": len(df), "exceedances": int(exceed), "top_locations": top}
```

#### `app/agents/policy_agent.py`

```python
from app.ollama_client import OllamaClient

async def draft_policy(model: str, city: str, analytics_summary: dict):
    oc = OllamaClient()
    prompt = f"""
You are a public health policy advisor for {city}.
Data summary: {analytics_summary}
Write a concise advisory for municipal stakeholders: 3 actions for transport emissions, 3 for indoor air, and 3 for community alerts. Include quick wins and medium-term actions.
"""
    return await oc.generate(model=model, prompt=prompt, temperature=0.2)
```

#### `app/agents/eval_agent.py`

```python
from app.ollama_client import OllamaClient

async def evaluate_policy(model: str, policy_text: str):
    oc = OllamaClient()
    rubric = """
Score the following policy (0–1) on clarity, feasibility, and expected impact. Return JSON:
{"clarity":float,"feasibility":float,"impact":float,"overall":float,"feedback":"..."}
"""
    resp = await oc.generate(model=model, prompt=rubric + "\n\n" + policy_text, temperature=0.0)
    return resp
```

#### `app/agents/supervisor.py` (LangGraph workflow with a simple loop)

```python
from typing import TypedDict, Any
from langgraph.graph import StateGraph, END

class State(TypedDict):
    city: str
    country: str
    parameter: str
    measurements: Any
    analytics: Any
    policy: str
    score: float

# Nodes
async def etl_node(state: State, fetch_fn):
    data = await fetch_fn(country=state.get("country"), city=state.get("city"), parameter=state.get("parameter", "pm25"))
    state["measurements"] = data
    return state

def analytics_node(state: State, analyze_fn):
    state["analytics"] = analyze_fn(state["measurements"])
    return state

async def policy_node(state: State, policy_fn, model: str):
    state["policy"] = await policy_fn(model=model, city=state["city"], analytics_summary=state["analytics"])
    return state

async def eval_node(state: State, eval_fn, model: str):
    raw = await eval_fn(model=model, policy_text=state["policy"])
    # naive parse for "overall"
    import re, json
    try:
        j = json.loads(re.search(r'\{.*\}', raw, re.S).group(0))
        state["score"] = float(j.get("overall", 0.0))
    except Exception:
        state["score"] = 0.0
    return state

def build_graph(fetch_fn, analyze_fn, policy_fn, eval_fn, model: str="llama3:8b-instruct-q4"):
    g = StateGraph(State)
    g.add_node("etl", lambda s: etl_node(s, fetch_fn))
    g.add_node("analytics", lambda s: analytics_node(s, analyze_fn))
    g.add_node("policy", lambda s: policy_node(s, policy_fn, model))
    g.add_node("eval", lambda s: eval_node(s, eval_fn, model))
    g.add_edge("etl", "analytics")
    g.add_edge("analytics", "policy")
    g.add_edge("policy", "eval")

    # loop if score < 0.8
    def route(state: State):
        return "policy" if float(state.get("score", 0.0)) < 0.8 else END
    g.add_conditional_edges("eval", route)

    return g.compile()
```

#### `app/a2a/agent_card.json`

```json
{
  "name": "Air Quality Analytics Agent",
  "description": "Analyzes OpenAQ data and drafts policies for cities.",
  "version": "1.0.0",
  "skills": [
    {"id": "analyze_city_pm25", "name": "Analyze PM2.5 for a city", "tags": ["analytics","airquality"]}
  ],
  "capabilities": { "streaming": true, "pushNotifications": false },
  "authentication": { "schemes": ["public"] },
  "url": "/a2a"
}
```

> A2A defines **Agent Cards** and endpoints for `message/send`, `message/stream`, `tasks/get`; this stub is enough for discovery; full SDK examples exist (LangGraph + A2A). [\[docs.langchain.com\]](https://docs.langchain.com/langsmith/server-a2a), [\[a2a-protocol.org\]](https://a2a-protocol.org/latest/tutorials/python/7-streaming-and-multiturn/)

#### `app/a2a/server.py` (minimal stub)

```python
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
import json
from pathlib import Path

router = APIRouter()

@router.get("/.well-known/agent-card.json")
async def agent_card():
    card = json.loads(Path(__file__).with_name("agent_card.json").read_text())
    return JSONResponse(card)

@router.post("/message/send")
async def message_send(req: Request):
    body = await req.json()
    # Expect { "input": { "city": "...", "country": "..."} }
    inp = body.get("input", {})
    return JSONResponse({"status": "accepted", "result": {"echo": inp}})
```

#### `app/observability/otel.py`

```python
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

def init_otel(app):
    FastAPIInstrumentor.instrument_app(app)  # traces; configure OTLP exporter via env vars [22](https://opentelemetry-python-contrib.readthedocs.io/en/latest/instrumentation/fastapi/fastapi.html)
```

#### `app/observability/metrics.py`

```python
from prometheus_fastapi_instrumentator import Instrumentator

def init_metrics(app):
    Instrumentator().instrument(app).expose(app)  # /metrics endpoint [29](https://dev.to/ken_mwaura1/getting-started-monitoring-a-fastapi-app-with-grafana-and-prometheus-a-step-by-step-guide-3fbn)
```

#### `app/main.py` (FastAPI gateway)

```python
from fastapi import FastAPI, Query
from app.settings import settings
from app.tools.openaq_api import fetch_measurements
from app.tools.bulk_ingest import list_archive, download_csv_gz
from app.agents.analytics_agent import analyze_measurements
from app.agents.policy_agent import draft_policy
from app.agents.eval_agent import evaluate_policy
from app.agents.supervisor import build_graph
from app.observability.otel import init_otel
from app.observability.metrics import init_metrics
from app.a2a.server import router as a2a_router

app = FastAPI(title="CleanAir Agents")
init_otel(app)
if settings.PROMETHEUS_ENABLED:
    init_metrics(app)

app.include_router(a2a_router, prefix="/a2a")

@app.get("/health")
def health(): return {"ok": True}

@app.get("/api/openaq")
async def openaq(city: str = Query(settings.DEFAULT_CITY), country: str = Query(settings.DEFAULT_COUNTRY)):
    return await fetch_measurements(country=country, city=city)

@app.get("/api/openaq-bulk")
async def openaq_bulk_sample():
    files = await list_archive()
    sample = await download_csv_gz(files[0])
    # return small head
    return {"file": files[0], "rows": sample[:10]}

@app.get("/api/analyze")
async def analyze(city: str = Query(settings.DEFAULT_CITY), country: str = Query(settings.DEFAULT_COUNTRY), model: str="llama3:8b-instruct-q4"):
    graph = build_graph(fetch_measurements, analyze_measurements, draft_policy, evaluate_policy, model=model)
    state = {"city": city, "country": country, "parameter": "pm25"}
    result = await graph.ainvoke(state)
    return {"analytics": result["analytics"], "policy": result["policy"], "score": result["score"]}
```

***

### 2.4 Observability (docker compose)

#### `infra/docker-compose.yml`

```yaml
version: "3.8"
services:
  prometheus:
    image: prom/prometheus:latest
    container_name: prometheus
    ports: [ "9090:9090" ]
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
  grafana:
    image: grafana/grafana:10.4.2
    container_name: grafana
    ports: [ "3000:3000" ]
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    depends_on:
      - prometheus
    volumes:
      - ./grafana:/var/lib/grafana
```

#### `infra/prometheus.yml`

```yaml
global:
  scrape_interval: 15s
scrape_configs:
  - job_name: 'fastapi'
    static_configs:
      - targets: [ 'host.docker.internal:8000', 'localhost:8000' ]
```

> FastAPI + Prometheus instrumentation is a standard pattern; Grafana has community dashboards for FastAPI. [\[dev.to\]](https://dev.to/ken_mwaura1/getting-started-monitoring-a-fastapi-app-with-grafana-and-prometheus-a-step-by-step-guide-3fbn), [\[grafana.com\]](https://grafana.com/grafana/dashboards/16110-fastapi-observability/)

*(Optional)* import a dashboard JSON under `infra/grafana/dashboards.json` (you can use Grafana’s “FastAPI Observability” reference). [\[grafana.com\]](https://grafana.com/grafana/dashboards/16110-fastapi-observability/)

***

### 2.5 Deployment

#### `deploy/Dockerfile`

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app ./app
ENV PORT=8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### `deploy/render.yaml`

```yaml
services:
  - type: web
    name: clean-air-agents
    env: python
    region: frankfurt
    buildCommand: "pip install -r requirements.txt"
    startCommand: "uvicorn app.main:app --host 0.0.0.0 --port 8000"
    healthCheckPath: "/health"
```

> Render’s free tier supports web services but **spins down** after 15 minutes of inactivity; ideal for demos. [\[render.com\]](https://render.com/docs/free)

#### `deploy/cloudrun.yaml`

```yaml
apiVersion: serving.knative.dev/v1
kind: Service
metadata:
  name: clean-air-agents
spec:
  template:
    spec:
      containers:
        - image: gcr.io/YOUR_PROJECT/clean-air-agents:latest
          ports: [{containerPort: 8000}]
          env:
            - name: PROMETHEUS_ENABLED
              value: "true"
      containerConcurrency: 1
```

> Cloud Run has an **always-free** tier (e.g., 180k vCPU‑seconds/month + 1 GiB egress NA), charging only for used compute beyond free quotas. [\[cloud.google.com\]](https://cloud.google.com/run/pricing), [\[freetiers.com\]](https://www.freetiers.com/directory/google-cloud-run)

***

### 2.6 React client (Vite)

#### `client/package.json`

```json
{
  "name": "clean-air-agents-client",
  "private": true,
  "version": "0.1.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "react": "18.3.1",
    "react-dom": "18.3.1",
    "ky": "1.4.0"
  },
  "devDependencies": {
    "vite": "5.4.8",
    "@vitejs/plugin-react": "4.3.2"
  }
}
```

#### `client/vite.config.js`

```js
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
export default defineConfig({
  plugins: [react()],
  server: { port: 5173, proxy: { '/api': 'http://localhost:8000', '/a2a': 'http://localhost:8000' } }
})
```

#### `client/src/api.js`

```js
import ky from 'ky'
const api = ky.create({ prefixUrl: '/api' })
export const fetchCity = (city, country='ZA') => api.get('openaq', { searchParams: { city, country } }).json()
export const analyzeCity = (city, country='ZA') => api.get('analyze', { searchParams: { city, country } }).json()
```

#### `client/src/main.jsx`

```jsx
import React from 'react'
import { createRoot } from 'react-dom/client'
import App from './App.jsx'
createRoot(document.getElementById('root')).render(<App />)
```

#### `client/src/App.jsx`

```jsx
import React, { useState } from 'react'
import { fetchCity, analyzeCity } from './api'

export default function App() {
  const [city, setCity] = useState('Johannesburg')
  const [country, setCountry] = useState('ZA')
  const [results, setResults] = useState(null)
  const [analysis, setAnalysis] = useState(null)
  return (
    <div style={{ padding: 20, fontFamily: 'system-ui' }}>
      <h2>CleanAir Agents — Johannesburg-first</h2>
      <div>
        <input value={city} onChange={e => setCity(e.target.value)} />
        <input value={country} onChange={e => setCountry(e.target.value)} style={{ marginLeft: 8 }} />
        <button onClick={async () => setResults(await fetchCity(city, country))} style={{ marginLeft: 8 }}>Fetch</button>
        <button onClick={async () => setAnalysis(await analyzeCity(city, country))} style={{ marginLeft: 8 }}>Analyze</button>
      </div>
      <pre style={{ marginTop: 20, background: '#f6f8fa', padding: 12 }}>
        {results && JSON.stringify(results, null, 2)}
      </pre>
      <pre style={{ marginTop: 12, background: '#f6f8fa', padding: 12 }}>
        {analysis && JSON.stringify(analysis, null, 2)}
      </pre>
      <p style={{ marginTop: 12, color: '#555' }}>
        Data courtesy of OpenAQ. [14](https://openaq.org/)
      </p>
    </div>
  )
}
```

***

## 3) Spin‑up steps for your Azure VM

1.  **Create VM**  
    Pick **B2s v2 (2 vCPU/8 GiB)**—or **D2\_v5** for steadier CPU. Both meet minimal RAM for 7–8B quantized models under Ollama (≥8 GB). [\[cloudprice.net\]](https://cloudprice.net/vm/Standard_B2s_v2), [\[learn.microsoft.com\]](https://learn.microsoft.com/en-us/azure/virtual-machines/sizes/general-purpose/dv5-series), [\[ollama.com\]](https://ollama.com/library/llama2:7b)

2.  **SSH in, install base**
=======
## Requirements
- Python 3.11+
- **Ollama** running locally (e.g., `ollama serve`) with a quantized 7–8B model like `llama3:8b-instruct-q4`.  
  7B/8B models typically need ≥ 8 GB RAM; quantization reduces memory footprint for CPU-only VM. [1](https://www.vroble.com/2025/11/taming-agentic-storm-mastering.html) [2](https://signoz.io/blog/opentelemetry-fastapi/)
>>>>>>> fed6c59 (agent mvp1 working locally)

## Quick start
```bash
# 1) Create venv and install deps
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 2) Run backend
uvicorn app.main:app --host 0.0.0.0 --port 8000
<<<<<<< HEAD
```

5.  **Run client**

```bash
cd client && npm i && npm run dev
# open http://<vm-public-ip>:5173 (configure NSG/firewall)
```

6.  **Observability (optional)**

```bash
cd infra && docker compose up -d
# Grafana at http://<vm-public-ip>:3000 (admin/admin); add Prometheus as data source
```

***

## 4) Notes & next steps

*   **OpenAQ API & bulk**: We wired both (API `v2/measurements` and S3 daily CSVs) so your pipeline works even if one approach stalls temporarily. [\[registry.o...endata.aws\]](https://registry.opendata.aws/openaq/), [\[openaq.org\]](https://openaq.org/)

*   **A2A**: The stub provides discovery; if you want a full agent server with streaming/multiturn and task stores, follow the LangGraph+A2A examples and SDKs. [\[docs.langchain.com\]](https://docs.langchain.com/langsmith/server-a2a), [\[a2a-protocol.org\]](https://a2a-protocol.org/latest/tutorials/python/7-streaming-and-multiturn/)

*   **Observability**: FastAPI + **OpenTelemetry** instrumentation (traces) and **Prometheus/Grafana** (metrics) are standard; Grafana has a “FastAPI Observability” dashboard ready to import. [\[openteleme...thedocs.io\]](https://opentelemetry-python-contrib.readthedocs.io/en/latest/instrumentation/fastapi/fastapi.html), [\[grafana.com\]](https://grafana.com/grafana/dashboards/16110-fastapi-observability/)

*   **Model choices**: Ollama’s library lists **Llama 3/3.1**, **Mistral**, **Qwen**, **Gemma**, **Phi**, etc. Start with `llama3:8b-instruct-q4` for stability on 8 GB RAM. [\[ollama.com\]](https://ollama.com/library)

***
=======

# 3) Try endpoints
curl 'http://localhost:8000/health'
curl 'http://localhost:8000/api/openaq?city=Johannesburg&country=ZA'
curl 'http://localhost:8000/api/analyze?city=Johannesburg&country=ZA&model=llama3:8b-instruct-q4'
>>>>>>> fed6c59 (agent mvp1 working locally)
