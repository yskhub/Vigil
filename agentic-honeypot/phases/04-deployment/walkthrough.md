# Phase 04 — Deployment Walkthrough

Status: Planned

Goals:
- Containerize the app and deploy to a cloud hosting provider.
- Configure HTTPS, environment variables, and secrets management.
- Set up Redis and background worker for GUVI callbacks.

Planned steps:
1. Build Docker image and push to registry.
2. Deploy to a small cloud instance or container service.
3. Configure `GUVI_CALLBACK_URL`, `API_KEY`, and `LLM_API_KEY`.
4. Validate public endpoint with `ngrok` or direct HTTPS.

Acceptance criteria:
- Live endpoint accessible over HTTPS.
- Callback worker can reach GUVI endpoint and handle retries.