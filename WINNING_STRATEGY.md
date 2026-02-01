# Winning Strategy for Agentic Honey-Pot Challenge

## 1. The Strategy: "The Confused Grandma" Persona
We have shifted the agent from a generic "Helpful Assistant" to **Martha**, a confused 68-year-old retired teacher.
**Why this wins:**
- **Believability**: Scammers target the elderly. This persona matches their ideal victim profile.
- **Engagement Duration**: Martha moves slowly, makes typos, and asks clarifying questions ("is it the green app?"). This forces the scammer to explain more, increasing the conversation turns (`totalMessagesExchanged`) and keeping the session active longer.
- **Extraction**: By asking "Which account number?" or "Can you send the link again?", we naturally extract intelligence without raising suspicion.

## 2. Technical Compliance (The "Must-Haves")
We have verified the following critical compliance points:
- [x] **API Auth**: `x-api-key` is enforcing security.
- [x] **Schema**: `extractedIntelligence` now includes `suspiciousKeywords` (e.g., "urgent", "verify now") as required by the grading prompt.
- [x] **Callback**: The `GUVI` callback endpoint is integrated and fires automatically upon session finalization.
- [x] **Latency**: The API is lightweight (FastAPI + Async) to ensure `engagementDurationSeconds` is tracked accurately without lag.

## 3. Deployment Plan (Execute Immediately)
To complete the "First Submission" and "Final Submission", we need a live public URL.

### Option A: Render (Recommended for Hackathons)
1. **Create Account**: Go to [dashboard.render.com](https://dashboard.render.com).
2. **New Web Service**: Connect your GitHub repo.
3. **Settings**:
    - **Runtime**: Python 3
    - **Build Command**: `pip install -r agentic-honeypot/src/requirements.txt`
    - **Start Command**: `uvicorn agentic-honeypot.src.main:app --host 0.0.0.0 --port 10000`
    - **Environment Variables**:
        - `API_KEY`: (Generate a strong key)
        - `OPENAI_API_KEY`: (Your OpenAI Key)
        - `GUVI_CALLBACK_URL`: `https://hackathon.guvi.in/api/updateHoneyPotFinalResult`
        - `PYTHONPATH`: `.`

### Option B: Self-Host (Ngrok / VPS)
If you have a VPS or want to test locally with a public URL:
1. Run: `uvicorn src.main:app --reload`
2. Run: `ngrok http 8000`
3. Use the `https://....ngrok-free.app` URL for the submission.

## 4. Final Verification Steps
Before submitting:
1. **Test the Endpoint**: Use the `First Submission` tester tool provided by the organizers.
2. **Verify JSON**: Ensure the response to that tester is `200 OK` and valid JSON.
3. **Check Callback**: Manually trigger a finalized session and check strict adherence to the `GUVI` payload format.

## 5. "Flash" UI (Bonus)
Since the UI requirement is minimal for the API track, the **Static HTML** dashboard we prepared (`ui/index.html`) is sufficient to show judges "conceptually" how it looks. Host it on GitHub Pages if asked for a demo link.
