# Environment Variables

This document explains the environment variables required to run the Agentic Honey-Pot prototype.

Required
- `API_KEY` — string. The API key used by clients to call the backend. This must be set in your deployment environment (Render, Docker, etc.). The application falls back to `secret-key` only when `API_KEY` is not set (development only).

Recommended
- `REDIS_URL` — string. If set, the app will use Redis for session persistence.
- `CALLBACK_URL` — string. Optional external callback endpoint to receive finalized session payloads.

Local development
- Create a `.env` file (do NOT commit) with:

```
API_KEY=your-secret-key-here
REDIS_URL=redis://localhost:6379/0
CALLBACK_URL=https://example.com/callback
```

On Windows (PowerShell):

```powershell
$env:API_KEY = "your-secret-key-here"
uvicorn src.main:app --reload
```

On CI (GitHub Actions)
- Add `API_KEY` as a repository secret and reference it in workflows.

Security notes
- Never commit secrets. Use your platform's secret store (Render env vars, GitHub Secrets, etc.).
