# Agentic Honeypot UI

Minimal Streamlit demo for sending test events to the backend.

Run locally (from repo root, with your virtualenv activated):

```powershell
pushd agentic-honeypot/ui
pip install streamlit requests
streamlit run app.py
popd
```

Fill `Backend base URL` (example: `https://your-backend.example.com`) and `x-api-key`, then click `Send message`.
Agentic Honey-Pot — Static UI

This is a minimal static demo UI that can be hosted on GitHub Pages.

Usage:
- Edit `index.html` to set `apiUrl` and `apiKey` or use the defaults.
- Serve locally with any static server, or push to `gh-pages` via the provided workflow.

This UI is intentionally minimal to avoid build steps or paid hosting.
