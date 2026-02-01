## Deploying the backend to Render (quick guide)

1) Prepare repository
- Ensure your repo is pushed to GitHub and includes the `agentic-honeypot/render.yaml` file (already added).

2) Create a new Web Service on Render
- Go to https://render.com and sign in.
- Click New → Web Service → Connect a repository and select this repo.
- Render will detect the `render.yaml` and present the `agentic-honeypot-api` service.

3) Build & Start (if Render asks)
- Build Command: `pip install -r agentic-honeypot/src/requirements.txt`
- Start Command: `uvicorn src.main:app --host 0.0.0.0 --port $PORT`

4) Environment variables / secrets
- Set `API_KEY` (required by the API). Save it as a Secret in Render (the `render.yaml` references it).
- Optionally set `REDIS_URL` if you want a managed Redis instance (Render add-on) or point to an external Redis.
- `LLM_PROVIDER` defaults to `mock` for free usage; set to `openai` only if you provide OpenAI keys.

5) Health check
- The service uses `/health` to validate readiness (defined in `render.yaml`).

6) Optional: Add Redis
- In Render, add the Redis managed service and set `REDIS_URL` to the provided connection string.

7) Accessing the Streamlit UI
- Deploy the Streamlit UI separately (Streamlit Community Cloud or a small Render static site) and point its `BACKEND_URL` to the Render service URL.

Notes
- The `render.yaml` sets `plan: free` and `region: oregon`; change those to match your preferences.
- If you want me to trigger the deploy, grant Render access to the repo and tell me to proceed; I can also provide a `render` CLI command snippet.
