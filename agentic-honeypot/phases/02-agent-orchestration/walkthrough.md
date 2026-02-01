# Phase 02 — Agent & Orchestration Walkthrough

Status: Planned / In progress

Goals:
- Integrate an LLM (OpenAI or alternative) as the agent backend.
- Implement Conversation Manager to maintain `sessionId` state, ordering, and timeouts.
- Add persona and pacing controls, stop criteria, and extraction hooks during conversation.

Planned steps:
1. Add `redis` dependency and session store implementation.
2. Implement `AgentOrchestrator` class to call LLM with system prompts, persona, and conversational history.
3. Add message queuing for long-running sessions.
4. Add instrumentation and guardrails for cost and safety.

Acceptance criteria:
- Agent can be invoked for a detected scam conversation and send follow-up messages.
- Extracted intelligence is accumulated in session state.