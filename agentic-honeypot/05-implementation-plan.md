# 05 — Implementation Plan

## Phase 1 — Prototype (1-2 days)
- Implement `POST /events` skeleton with API key check.
- Add rule-based scam detector (keywords, urgency patterns).
- Build a stub Agent that replies with canned messages.
- Implement simple extractor (regex: UPI, phone, URLs).
- Local test harness to simulate convo flows.

## Phase 2 — Agent & Orchestration (2-4 days)
- Integrate an LLM (or local model) for dynamic responses.
- Implement Conversation Manager and session store (Redis or in-memory).
- Add persona and pacing controls.
- Add metrics and logging.

## Phase 3 — Robustness & Testing (2 days)
- Add unit/integration tests for API and extraction.
- Implement retry/backoff for GUVI callback worker.
- Add rate-limiting and input validation.

## Phase 4 — Deployment & Demo (1-2 days)
- Containerize app (Dockerfile).
- Deploy to cloud (Azure/GCP/AWS) or use Replit/Render for quick demo.
- Provide public HTTPS endpoint and test with evaluation flow.

## Phase 5 — Polish
- Tune detector (ML model if time allows).
- Optimize token usage and cost controls for LLM.
- Prepare final demo script and documentation.

## Deliverables
- Running REST API with API key protection.
- Agent that can perform multi-turn engagements and extract intelligence.
- GUVI final callback integration.
- Phase docs in project folder.

## Next immediate steps
1. Start Phase 1: scaffold codebase and implement `POST /events`.
2. Add simple rule-based detector and extractor.
3. Create local test harness to simulate messages.