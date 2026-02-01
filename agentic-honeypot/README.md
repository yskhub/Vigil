# Agentic Honeypot — Hackathon PRD Implementation

This workspace contains a prototype implementation for the "Agentic Honey-Pot for Scam Detection & Intelligence Extraction" PRD. It includes a FastAPI backend, optional agent integrations (mock/OpenAI/local LLM), Redis-capable session store with in-memory fallback, auto-finalizer, callback worker, tests, and a Streamlit demo UI.

Quick start (development):

- Create and activate a Python 3.11+ virtualenv.
- pip install -r src/requirements.txt
- (Optional) pip install -r ui/requirements-streamlit.txt for the Streamlit UI.
- Run the API: `uvicorn src.main:app --reload --port 8000`
- Open `ui/streamlit_app.py` with Streamlit: `streamlit run ui/streamlit_app.py`

See docs/ for deployment and optional local-LLM instructions.
# Agentic Honey-Pot — Project Scaffold

This folder contains phase-by-phase documentation to build the Agentic Honey-Pot for the hackathon.

Files:
- `01-requirements.md` — Functional & non-functional requirements.
- `02-architecture.md` — Architecture and data flow.
- `03-api-spec.md` — API request/response and authentication.
- `04-agent-design.md` — Agent persona, flow, extraction strategy.
- `05-implementation-plan.md` — Step-by-step implementation plan.
- `06-deployment.md` — Deployment notes and env vars.

Next steps:
1. Implement Phase 1 prototype in `src/`.
2. Create tests and CI.
3. Deploy and run evaluation flow.

If you'd like, I can now scaffold the `src/` prototype (FastAPI/Flask/Express) and implement the initial rule-based detector. Which stack do you prefer? (Python FastAPI recommended)