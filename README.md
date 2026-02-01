# Agentic HoneyPot — Run & Deploy

Quick start (local venv):

```powershell
& .venv\Scripts\Activate.ps1
pip install -r requirements.txt
cd agentic-honeypot
python -m uvicorn src.main:app --port 8000
```

Run tests:

```powershell
D:/Vigil/.venv/Scripts/python.exe -m pytest -q
```

Build Docker image:

```bash
docker build -t agentic-honeypot:latest .
docker run -p 8000:8000 -e API_KEYS="secret-key" agentic-honeypot:latest
```

Smoke tests and rotation:

```bash
python scripts/smoke_test_deploy.py --url http://127.0.0.1:8000 --api-key secret-key
python scripts/rotate_keys.py --url http://127.0.0.1:8000 --admin-key secret-key newkey1 newkey2
```

CI / Docker

- A GitHub Actions workflow `CI / Test / Docker` is present at `.github/workflows/ci-docker.yml`. It runs tests (with a Redis service), performs a `gitleaks` secret scan, builds a Docker image, and can push to GitHub Container Registry when `GHCR_TOKEN` is set in repo secrets.

To enable pushing image to GHCR:

1. Create a personal access token with `write:packages` and add it as repository secret `GHCR_TOKEN`.
2. The workflow will push to `ghcr.io/<owner>/agentic-honeypot:latest` when `GHCR_TOKEN` is present.

Render deploy

- A GitHub Actions workflow `.github/workflows/deploy-render.yml` will trigger a Render deploy when repository secrets `RENDER_API_KEY` and `RENDER_SERVICE_ID` are set.
- To deploy via CI, create a Render service with your Docker image or set the service to deploy from the repository. Store `RENDER_API_KEY` and `RENDER_SERVICE_ID` in repo secrets.
- To deploy via CI, create a Render service with your Docker image or set the service to deploy from the repository. Store `RENDER_API_KEY` and `RENDER_SERVICE_ID` in repo secrets.

CI smoke tests

- The CI workflow includes an optional `smoke` job which will run `scripts/smoke_test_deploy.py` after the build if repository secrets `BACKEND_URL` and `BACKEND_API_KEY` are configured. This lets CI run a quick end-to-end check against a deployed backend.

Docs:
- `docs/monitoring.md` — Prometheus metrics
- `docs/key_rotation.md` — rotation procedure
- `docs/grafana_alerts.md` — Grafana example
