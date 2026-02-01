# Phase 01 — Prototype Walkthrough

Status: Completed (local prototype)

What this phase delivered:
- `POST /events` FastAPI endpoint (`src/main.py`).
- Rule-based scam detector (keyword matching).
- Simple extractor: UPI regex, phone regex, URL regex, account-like numbers.
- `test_client.py` to exercise the endpoint locally.
- `Dockerfile` and `requirements.txt` for containerized run.

How to run locally:

1. create a venv and install requirements

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r src\requirements.txt
uvicorn src.main:app --reload --port 8000
```

2. In another terminal run the test client:

```powershell
python src\test_client.py
```

Notes & Next steps for Phase 2:
- Integrate LLM for autonomous agent responses.
- Add Conversation Manager and session store (Redis).
- Add GUVI callback worker logic.