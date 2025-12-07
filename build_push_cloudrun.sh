# From project root
docker build -f deploy/Dockerfile -t gcr.io/agentic_environmental_management/clean-air-agents:latest .
docker push gcr.io/agentic_environmental_management/clean-air-agents:latest
gcloud run deploy clean-air-agents \
  --image gcr.io/agentic_environmental_management/clean-air-agents:latest \
  --platform managed --region YOUR_REGION --allow-unauthenticated
