# Agentic Honey-Pot: Complete Development & Submission Guide

This document outlines the entire lifecycle of the **Vigil Agentic Honey-Pot** project, from initial design phases to final deployment and hackathon submission.

---

## 1. Project Overview & Phases

### Phase 1: Prototype (Foundation)
*   **Goal**: Create a basic REST API that can accept messages and detect scams using rule-based logic.
*   **What We Built**:
    *   `POST /events` endpoint using **FastAPI**.
    *   `src/main.py`: The core application server.
    *   `detect_scam()`: Uses keyword analysis (e.g., "urgent", "verify") to flag messages.
    *   `extract_from_text()`: Regex-based extraction for UPI IDs, URLs, and phone numbers.

### Phase 2: Agent Orchestration (The "Brain")
*   **Goal**: enable the system to reply autonomously to scammers.
*   **What We Built**:
    *   `src/agent.py`: Integrated **OpenAI** (GPT-3.5) with a custom system prompt.
    *   **Persona "Martha"**: Designed a specific persona (68-year-old retired teacher, confused but willing) to prolong engagement.
    *   **Session Management**: `src/session_store.py` to track conversation history per `sessionId`.

### Phase 3: Compliance & Intelligence (The "Winning Logic")
*   **Goal**: Ensure strict adherence to the Hackathon's 10-point checklist.
*   **What We Built**:
    *   **Extracted Intelligence**: Added `suspiciousKeywords` extraction to satisfy the GUVI callback schema.
    *   **Callback Worker**: Implemented `send_final_callback()` to report results to `hackathon.guvi.in`.
    *   **Latency Handling**: Optimized async processing to ensure fast API responses.

### Phase 4: Production Deployment
*   **Goal**: Make the API public via HTTPS for the judges.
*   **What We Built**:
    *   `requirements.txt`: Locked dependencies (FastAPI, Uvicorn, Requests, OpenAI).
    *   **Render Deployment**: Configured a cloud web service running Python 3.

---

## 2. Technical Implementation Details

### Core Technologies
*   **Language**: Python 3.11+
*   **Framework**: FastAPI (High performance, clean JSON validation)
*   **Agent**: OpenAI API (`gpt-3.5-turbo`)
*   **Server**: Uvicorn (ASGI)
*   **Hosting**: Render (Cloud Platform)

### Key Files
*   `src/main.py`: Entry point. Handles auth, rate limiting, and request routing.
*   `src/agent.py`: Defines the "Martha" persona and generates safe, non-revealing replies.
*   `src/session_store.py`: In-memory implementation (with Redis fallback) to store chat logs.

---

## 3. How to Test Locally (Self-Validation)

Before submitting, you should always verify your endpoint works.

### Step 1: Endpoint Tester Script
Run the following PowerShell command to mimic the Judge's test:

```powershell
$key = "Agentic_Honey_Pot_Scam_Detection_Intelligence_Extraction_2026_X1"

# Mimic a "First Message" from a scammer
$body = @{
    sessionId = "manual-test-live-1"
    message = @{
        sender = "scammer"
        text = "URGENT: Your bank account is blocked. Verify at http://fake-bank.com immediately."
    }
    conversationHistory = @()
    metadata = @{ channel = "SMS" }
} | ConvertTo-Json -Depth 5

# Send Request
Invoke-RestMethod -Uri "https://vigil-889d.onrender.com/events" -Method Post -Headers @{"x-api-key"=$key; "Content-Type"="application/json"} -Body $body
```

### Step 2: Verification Checklist
1.  **Status Code**: `200 OK`.
2.  **scamDetected**: `True`.
3.  **extractedIntelligence**: Must verify `suspiciousKeywords` contains `["urgent", "verify", "blocked"]`.
4.  **agentReply**: Must be text in the voice of "Martha" (e.g., *"Oh dear, I clicked the link but nothing happened..."*).

---

## 4. First Submission Rules (Honeypot Endpoint Tester)

**Objective**: Verify your API is reachable and secured.

### Submission Steps
1.  Go to the **First Submission** page on the Hackathon portal.
2.  **Endpoint URL**: Paste your Render URL:
    `https://vigil-889d.onrender.com/events`
3.  **API Key**: Paste your exact Environment Variable key:
    `Agentic_Honey_Pot_Scam_Detection_Intelligence_Extraction_2026_X1`
4.  **Click "Test"**:
    *   The system sends a ping request.
    *   Your API validates the key.
    *   **Success**: You will see a green checkmark or success message.

---

## 5. Final Submission Rules (The Real Contest)

**Objective**: The system acts as a fully automated agent to trick scammers.

### Submission Steps
1.  Go to the **Final Submission** page.
2.  **Endpoint URL**: Use the same URL: `https://vigil-889d.onrender.com/events`
3.  **API Key**: Use the same Key: `Agentic_Honey_Pot_Scam_Detection_Intelligence_Extraction_2026_X1`
4.  **Submit**:
    *   The Automated Evaluation System will immediately start sending attack scenarios to your API.
    *   It will check if you extract intelligence and fire the GUVI callback.

### What Happens Next?
*   **Automated Attacks**: The system will simulate different scams (UPI fraud, Phishing, Bank KYC).
*   **Your "Martha" Persona**: Will engage, ask "confused" questions, and prolong the chat.
*   **Grading**:
    *   Did you detect the scam? (Yes)
    *   Did you extract the UPI/URL? (Yes)
    *   Did you report it securely? (Yes)
    *   Did the conversation last >12 message turns? (Likely, due to the persona).

---

## 6. Troubleshooting

*   **404 Not Found**: If you visit the root URL (`/`) in a browser. **Normal**. The API is at `/events`.
*   **Unauthorized**: Check that the API Key in the submission form **matches** the `API_KEY` variable in Render exactly.
*   **Server Error 500**: Check Render logs. Usually implies an import error (fixed by adding `prometheus_client` earlier).

**Good Luck! You are fully prepared.**
