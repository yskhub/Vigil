# 04 — Agent Design

## Persona
- Friendly, slightly helpful, plausible human tone.
- Avoid explicit claims of detection or monitoring.
- Use conversational language localized to `metadata.locale`.

## Conversation Flow
- Warm, non-committal responses to gather information (e.g., "Can you share the payment method you prefer?").
- Use probing questions to elicit intelligence: payment handles, links, phone numbers.
- Use delays and typing-like pacing to remain human-like.

## Safety & Ethics Rules
- Never impersonate real persons.
- Do not request illegal actions (directed money transfer) — steer conversation to gather passive intel instead.
- If scammer becomes abusive, politely disengage.

## Multi-turn Handling
- Maintain short-term memory per session; summarize recent context when needed.
- Implement guardrails: max messages or time per session; fallback to graceful close.

## Extraction Strategy
- After each incoming message, run extraction patterns (regex for UPI, phone, URLs) and NER.
- Accumulate extracted items in session store and dedupe.

## Stop Criteria
- No new intelligence after N turns (configurable), or
- Conversation length exceeds threshold, or
- Agent confidence that key intelligence obtained.

## Logging & Telemetry
- Log message timestamps, agent decisions, extracted entities (masked when necessary).
- Track engagement metrics for evaluation.