# 06 — Deployment

## Recommended Setup
- Containerize service with `Docker`.
- Use a small Redis instance for session state.
- Background worker for GUVI callback and long-running agent sessions.

## Environment Variables
- `API_KEY` — incoming request key
- `GUVI_CALLBACK_URL` — https://hackathon.guvi.in/api/updateHoneyPotFinalResult
- `LLM_API_KEY` — key for LLM provider (if used)
- `REDIS_URL` — session store
- `RETENTION_DAYS` — session retention policy

## Local Testing
- Use `ngrok` for exposing local HTTPS endpoint for quick demo.

## Docker (example)
- Build: `docker build -t agentic-honeypot .`
- Run: `docker run -e API_KEY=secret -p 8080:8080 agentic-honeypot`

## CI/CD
- Run tests, build image, push to registry, deploy to cloud.

## Observability
- Export metrics (Prometheus) and basic logs to a central store.

## Security
- Enforce HTTPS and strong API key management.
- Mask sensitive intelligence in logs (store minimal masked values).