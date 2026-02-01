# 01 — Requirements

## Functional Requirements
- Accept incoming message events via REST API (`POST /events`).
- Authenticate requests using `x-api-key` header.
- Detect scam/fraud intent (first message or follow-ups).
- When scam intent detected, activate an autonomous AI Agent to engage.
- Maintain believable human-like persona across multi-turn conversation.
- Extract structured intelligence (bank accounts, UPI IDs, links, phone numbers, suspicious keywords).
- Return structured JSON response and send final callback to GUVI endpoint after engagement completes.

## Non-Functional Requirements
- Low latency for detection (prefer <1s for initial classification).
- Stable API with clear error codes.
- Secure storage of extracted intelligence and keys.
- Respect ethics constraints (no impersonation, no illegal instructions).

## Data & Security
- API key in header: `x-api-key`.
- Store session transcripts temporarily; purge after reporting per retention policy.
- Use HTTPS in deployment.

## Mandatory Callback (GUVI)
- POST to `https://hackathon.guvi.in/api/updateHoneyPotFinalResult` with required payload only after engagement and extraction complete.

## Acceptance Criteria
- API accepts events and returns JSON in required schema.
- Agent engages and obtains at least one intelligence item in tests.
- Final callback is sent after session completion.