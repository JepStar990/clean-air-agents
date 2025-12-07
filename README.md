
# CleanAir Agents — Johannesburg-first, globally-ready

A multi-agent FastAPI application that pulls **OpenAQ** air-quality data (API + bulk), analyzes local PM2.5 trends for Johannesburg (or any city), and drafts short policy advisories using a local LLM via **Ollama**. Observability hooks (OpenTelemetry + Prometheus) are included.

## Why OpenAQ?
OpenAQ aggregates global air-quality measurements and exposes them via an open API and a daily S3 CSV archive—ideal for sustainability analysis and repeatable UAT.  
- API & registry details: https://registry.opendata.aws/openaq/ (S3 archive, hourly updates) [3](https://huggingface.co/docs/hub/spaces)  
- Platform overview & mission: https://openaq.org/ [4](https://huggingface.co/docs/hub/advanced-compute-options)

## Requirements
- Python 3.11+
- **Ollama** running locally (e.g., `ollama serve`) with a quantized 7–8B model like `llama3:8b-instruct-q4`.  
  7B/8B models typically need ≥ 8 GB RAM; quantization reduces memory footprint for CPU-only VM. [1](https://www.vroble.com/2025/11/taming-agentic-storm-mastering.html) [2](https://signoz.io/blog/opentelemetry-fastapi/)

## Quick start
```bash
# 1) Create venv and install deps
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 2) Run backend
uvicorn app.main:app --host 0.0.0.0 --port 8000

# 3) Try endpoints
curl 'http://localhost:8000/health'
curl 'http://localhost:8000/api/openaq?city=Johannesburg&country=ZA'
curl 'http://localhost:8000/api/analyze?city=Johannesburg&country=ZA&model=llama3:8b-instruct-q4'
