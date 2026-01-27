# 02 — Architecture

## High-level Components
- REST API (Ingress)
  - Endpoint: `POST /events`
  - Auth: `x-api-key`
- Scam Detector
  - Lightweight classifier (rules + ML) to detect scam intent.
- Conversation Manager
  - Tracks `sessionId`, conversationHistory, message sequencing, timeouts.
- Agent Orchestrator
  - Controls the LLM-based agent, conversation policies, persona state.
- Intelligence Extractor
  - NLP extraction (regex, NER, pattern matching) for UPI IDs, accounts, links, phone numbers.
- Persistence
  - Short-term store for sessions (Redis or in-memory) and long-term audit logs (encrypted DB).
- Callback Worker
  - Sends final extracted intelligence to GUVI endpoint reliably (with retry/backoff).
- Monitoring & Security
  - Rate-limiting, request logging, API key management, metrics.

## Data Flow
1. Ingress receives event → authenticate
2. Scam Detector classifies message
3. If scamDetected=false: respond with `scamDetected:false` quickly
4. If scamDetected=true: spin Agent Orchestrator to engage via Conversation Manager
5. Agent exchanges messages (multi-turn) until stopping criteria
6. Intelligence Extractor populates structured output
7. API returns result and Callback Worker posts to GUVI

## Deployment Targets
- Containerized (Docker) service behind HTTPS load balancer.
- Simple initial deployment: single container + Redis (or in-memory) + background worker.

## Scaling Considerations
- Horizontal scale API and agent workers
- Queue-based orchestration for long-running engagements
- Cost control for LLM usage (budgeted tokens, sampling)