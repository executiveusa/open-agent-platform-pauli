# Runbook

## Local development
1. Copy `.env.example` to `.env` and set secrets.
2. Run `docker compose -f infra/docker/docker-compose.yml up --build`.
3. Open:
   - API: http://localhost:8000/api/health
   - Temporal UI: http://localhost:8080
   - Langfuse: http://localhost:3000
   - noVNC: http://localhost:6080/vnc.html

## Smoke test
Create a run:
```bash
curl -X POST http://localhost:8000/api/runs \
  -H 'Content-Type: application/json' \
  -d '{"agent_type":"demo","inputs":{"task":"ping"}}'
```
Stream events:
```bash
curl http://localhost:8000/api/runs/<run_id>/events
```

## Recovery workflow
Trigger healing:
```bash
curl -X POST http://localhost:8000/api/runs/<run_id>/heal
```
