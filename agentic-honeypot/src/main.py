from fastapi import FastAPI, Header, HTTPException, Request
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime
import os
import re

app = FastAPI(title="Agentic Honey-Pot Prototype")

API_KEY = os.getenv("API_KEY", "secret-key")

# Request models
class Message(BaseModel):
    sender: str
    text: str
    timestamp: datetime

class Event(BaseModel):
    sessionId: str
    message: Message
    conversationHistory: List[Dict[str, Any]] = []
    metadata: Dict[str, Any] = {}

# Simple rule-based detector
SCAM_KEYWORDS = [
    "verify", "account blocked", "will be blocked", "upi id", "share your", "bank account",
    "suspend", "suspension", "immediately", "urgent", "verify now", "password",
]

UPI_RE = re.compile(r"\b[\w.-]{2,}@[a-zA-Z]{2,}\b")
PHONE_RE = re.compile(r"(?:\+?\d{1,3}[\s-]?)?(?:\d{10}|\d{3}[\s-]\d{3}[\s-]\d{4})")
URL_RE = re.compile(r"https?://[\w./?=&%-]+|www\.[\w./?=&%-]+")
ACC_RE = re.compile(r"\b\d{6,20}\b")


def detect_scam(text: str) -> Dict[str, Any]:
    t = text.lower()
    matched = [k for k in SCAM_KEYWORDS if k in t]
    # If contains urgency keywords or payment/verification asks, mark as scam-suspect
    scam = len(matched) > 0
    return {"scam": scam, "matched_keywords": matched}


def extract_from_text(text: str) -> Dict[str, List[str]]:
    upis = list(set(UPI_RE.findall(text)))
    phones = list(set(PHONE_RE.findall(text)))
    urls = list(set(URL_RE.findall(text)))
    accounts = list(set(ACC_RE.findall(text)))
    # attempt to filter obvious false positives for accounts (e.g., timestamps)
    accounts = [a for a in accounts if len(a) >= 8]
    return {
        "bankAccounts": accounts,
        "upiIds": upis,
        "phishingLinks": urls,
        "phoneNumbers": phones,
    }


@app.post("/events")
async def handle_event(event: Event, x_api_key: Optional[str] = Header(None)):
    # Auth
    if x_api_key is None or x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized: invalid x-api-key")

    # Combine latest message + conversation history for extraction
    all_texts = []
    for msg in event.conversationHistory:
        txt = msg.get("text") if isinstance(msg, dict) else None
        if txt:
            all_texts.append(txt)
    all_texts.append(event.message.text)
    full_text = "\n".join(all_texts)

    detection = detect_scam(event.message.text)
    extracted = extract_from_text(full_text)

    # Basic engagement metrics (prototype)
    total_messages = len(event.conversationHistory) + 1
    engagement_seconds = 0
    try:
        timestamps = [datetime.fromisoformat(m.get("timestamp")) for m in event.conversationHistory if m.get("timestamp")]
        timestamps.append(event.message.timestamp)
        engagement_seconds = int((max(timestamps) - min(timestamps)).total_seconds()) if len(timestamps) > 1 else 0
    except Exception:
        engagement_seconds = 0

    agent_notes = []
    if detection["matched_keywords"]:
        agent_notes.append("Matched keywords: " + ", ".join(detection["matched_keywords"]))
    if any(extracted.values()):
        agent_notes.append("Extracted possible intelligence items.")

    response = {
        "status": "success",
        "scamDetected": detection["scam"],
        "engagementMetrics": {
            "engagementDurationSeconds": engagement_seconds,
            "totalMessagesExchanged": total_messages,
        },
        "extractedIntelligence": extracted,
        "agentNotes": " ".join(agent_notes) if agent_notes else "No flags detected.",
    }

    # Note: In Phase 1 prototype we do NOT spin up an autonomous LLM agent yet.
    # This endpoint returns detection + extraction results for the platform to evaluate.

    return response


@app.get("/health")
async def health():
    return {"status": "ok"}
