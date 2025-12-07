# ---- Stage 1: build React client ----
FROM node:20-alpine AS client-build
WORKDIR /client
COPY client/package.json client/vite.config.js ./
COPY client/src ./src
RUN npm ci && npm run build

# ---- Stage 2: backend ----
FROM python:3.11-slim AS backend
WORKDIR /app

# System deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl ca-certificates && rm -rf /var/lib/apt/lists/*

# Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# App source
COPY app ./app

# Copy client build to static dir served by FastAPI
RUN mkdir -p app/static
COPY --from=client-build /client/dist ./app/static

# Environment (override at deploy time)
ENV PORT=8000
# OPENAQ_API_KEY should be set by the platform for v3 API auth

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

