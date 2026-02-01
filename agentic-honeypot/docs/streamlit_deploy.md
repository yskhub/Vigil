# Deploying the Streamlit App (free options)

This project includes a Streamlit demo at `agentic-honeypot/ui/streamlit_app.py`.

Local run

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r agentic-honeypot/ui/requirements-streamlit.txt
streamlit run agentic-honeypot/ui/streamlit_app.py
```

Streamlit Community Cloud (free tier)
1. Create an account at https://streamlit.io/cloud.
2. Connect your GitHub repo and pick the `agentic-honeypot/ui` folder as the app location and `streamlit_app.py` as the entrypoint.
3. Set secrets in Streamlit Cloud settings for `BACKEND_URL` and `API_KEY` or use environment variables.

Hugging Face Spaces (Gradio/Streamlit)
- You can also host Streamlit apps on Hugging Face Spaces. Create a new Space, choose `Streamlit`, and push the UI folder.
- Add `requirements.txt` (or use `requirements-streamlit.txt`) to the Space.
- Use the Spaces secrets UI to set `BACKEND_URL` and `API_KEY`.

Security
- Do not store API keys in the code. Use Streamlit secrets or the platform's secret manager.
- For demos, set `BACKEND_URL` to a public FastAPI endpoint or an `ngrok` tunnel.

Notes
- Streamlit Community Cloud has free resources and may sleep when idle; it's best for demos and interactive exploration.
