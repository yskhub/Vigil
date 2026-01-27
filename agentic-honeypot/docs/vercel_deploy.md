# Deploying the static UI to Vercel with a serverless proxy

This guide deploys the UI and a serverless proxy to Vercel so the frontend does not store the `x-api-key` in browser code.

1. Sign in at https://vercel.com and connect your GitHub repository `yskhub/Vigil`.

2. When creating the project, set the "Root Directory" to `agentic-honeypot/ui` so Vercel deploys that folder.

3. Environment variables (set in Vercel Project Settings → Environment Variables):
- `BACKEND_URL` → e.g. `https://your-fastapi-host.example` (no trailing slash)
- `API_KEY` → the secret API key your FastAPI expects (this will be injected by the proxy)

4. The proxy path:
- The serverless function is at `/api/proxy/*` on the deployed site.
- In the UI, change the `API URL` to the proxy endpoint: `https://<your-vercel-domain>/api/proxy/events`.
- The proxy will forward `POST /api/proxy/events` to `{BACKEND_URL}/events` and add the `x-api-key` header.

5. Secure notes:
- Do NOT embed `API_KEY` in the client bundle. Keep it in Vercel env variables.
- The UI remains static and safe to host publicly.

6. Optional: If your backend requires HTTPS and public access, ensure `BACKEND_URL` is reachable by Vercel.

7. After deployment, Vercel provides preview URLs for PRs and a production URL for the `main` branch.

If you want, I can create a small example `vercel.json` or tweak the UI defaults for the proxy URL.
