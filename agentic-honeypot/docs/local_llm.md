# Running a Local LLM (optional, free but resource-dependent)

This project supports an optional local LLM provider using `transformers`.

1. Install local requirements (may be large):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r agentic-honeypot/requirements-local.txt
```

2. Configure the provider and model (environment variables):
- `LLM_PROVIDER=local`
- `LOCAL_LLM_MODEL=gpt2` (or another small model you choose)

3. Run the app as usual. The `AgentOrchestrator` will attempt to use the local model.

Notes:
- Running even `gpt2` locally requires disk space and some CPU; larger models may need GPU.
- If you don't want to use a local LLM, do not set `LLM_PROVIDER` and the system will use the mock agent (free).
