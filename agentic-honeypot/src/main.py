from fastapi import FastAPI, Header, HTTPException, Request
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime
import os
import re
import asyncio
from contextlib import asynccontextmanager

from session_store import SessionStore
from agent import AgentOrchestrator
from callback_worker import send_final_callback
from auto_finalizer import start_background_loop


@asynccontextmanager
async def lifespan(app: FastAPI):
    # start auto-finalizer background task (free-mode)
    loop = asyncio.get_event_loop()
    stop_event, task = start_background_loop(loop)
    try:
        yield
    finally:
        stop_event.set()
        try:
            await task
        except Exception:
            pass


app = FastAPI(title="Agentic Honey-Pot Prototype", lifespan=lifespan)

API_KEY = os.getenv("API_KEY", "secret-key")
API_KEYS = [k.strip() for k in os.getenv("API_KEYS", API_KEY).split(",") if k.strip()]

# simple in-memory rate limiter: {api_key: {window_start: timestamp, count: int}}
rate_table = {}
RATE_LIMIT = int(os.getenv("RATE_LIMIT_PER_MIN", "60"))


def check_api_key(key: Optional[str]) -> bool:
    return key in API_KEYS


def rate_limit_ok(key: str) -> bool:
    import time
    now = int(time.time())
    window = now // 60
    st = rate_table.setdefault(key, {})
    if st.get("window") != window:
        st["window"] = window
        st["count"] = 0
    if st["count"] >= RATE_LIMIT:
        return False
    st["count"] += 1
    return True

# init services
session_store = SessionStore()
agent = AgentOrchestrator()

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
    scam = len(matched) > 0
    return {"scam": scam, "matched_keywords": matched}


def extract_from_text(text: str) -> Dict[str, List[str]]:
    upis = list(set(UPI_RE.findall(text)))
    phones = list(set(PHONE_RE.findall(text)))
    urls = list(set(URL_RE.findall(text)))
    accounts = list(set(ACC_RE.findall(text)))
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
    if x_api_key is None or not check_api_key(x_api_key):
        raise HTTPException(status_code=401, detail="Unauthorized: invalid x-api-key")
    if not rate_limit_ok(x_api_key):
        raise HTTPException(status_code=429, detail="Rate limit exceeded")

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

    # Persist incoming message to session store
    await session_store.append_message(event.sessionId, {"sender": event.message.sender, "text": event.message.text, "timestamp": event.message.timestamp.isoformat()})
    # Merge any existing extracted intelligence
    prev_extracted = await session_store.get_extracted(event.sessionId)
    merged = {}
    for k in set(list(prev_extracted.keys()) + list(extracted.keys())):
        prev_list = prev_extracted.get(k, []) or []
        new_list = extracted.get(k, []) or []
        merged[k] = list(dict.fromkeys(prev_list + new_list))
    await session_store.set_extracted(event.sessionId, merged)

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
    if any(merged.values()):
        agent_notes.append("Extracted possible intelligence items.")

    # If scam is detected, activate the agent to generate a follow-up reply (prototype behavior)
    agent_reply = None
    if detection["scam"]:
        # fetch current history to pass to agent
        history = await session_store.get_history(event.sessionId)
        if not history or history[-1].get("text") != event.message.text:
            history.append({"sender": event.message.sender, "text": event.message.text, "timestamp": event.message.timestamp.isoformat()})
        agent_reply = await agent.generate_reply(event.sessionId, history, event.metadata)
        # persist agent reply
        await session_store.append_message(event.sessionId, agent_reply)

    response = {
        "status": "success",
        "scamDetected": detection["scam"],
        "engagementMetrics": {
            "engagementDurationSeconds": engagement_seconds,
            "totalMessagesExchanged": total_messages,
        },
        "extractedIntelligence": merged,
        "agentNotes": " ".join(agent_notes) if agent_notes else "No flags detected.",
    }

    if agent_reply:
        response["agentReply"] = agent_reply

    return response


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/sessions/{session_id}/finalize")
async def finalize_session(session_id: str, body: Dict[str, Any], x_api_key: Optional[str] = Header(None)):
    # Auth
    if x_api_key is None or not check_api_key(x_api_key):
        raise HTTPException(status_code=401, detail="Unauthorized: invalid x-api-key")
    if not rate_limit_ok(x_api_key):
        raise HTTPException(status_code=429, detail="Rate limit exceeded")

    scam_detected = bool(body.get("scamDetected", False))
    if not scam_detected:
        raise HTTPException(status_code=400, detail="scamDetected must be true to finalize")

    extracted = await session_store.get_extracted(session_id)
    total_messages = int(body.get("totalMessagesExchanged", 0))
    agent_notes = body.get("agentNotes", "")

    payload = {
        "sessionId": session_id,
        "scamDetected": True,
        "totalMessagesExchanged": total_messages,
        "extractedIntelligence": extracted,
        "agentNotes": agent_notes,
    }

    result = await send_final_callback(payload)
    return {"status": "callback_attempted", "result": result}


@app.get("/sessions")
async def list_sessions_endpoint(x_api_key: Optional[str] = Header(None)):
    if x_api_key is None or not check_api_key(x_api_key):
        raise HTTPException(status_code=401, detail="Unauthorized: invalid x-api-key")
    if not rate_limit_ok(x_api_key):
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    sessions = await session_store.list_sessions()
    out = []
    for s in sessions:
        extracted = await session_store.get_extracted(s)
        total = await session_store.get_total_messages(s)
        last = await session_store.get_last_seen(s)
        out.append({"sessionId": s, "totalMessages": total, "lastSeen": last, "extractedCount": sum(len(v) for v in extracted.values() if isinstance(v, list))})
    return {"status": "success", "sessions": out}


@app.get("/sessions/{session_id}")
async def get_session(session_id: str, x_api_key: Optional[str] = Header(None)):
    if x_api_key is None or not check_api_key(x_api_key):
        raise HTTPException(status_code=401, detail="Unauthorized: invalid x-api-key")
    if not rate_limit_ok(x_api_key):
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    history = await session_store.get_history(session_id)
    extracted = await session_store.get_extracted(session_id)
    finalized = await session_store.is_finalized(session_id)
    return {"status": "success", "sessionId": session_id, "history": history, "extractedIntelligence": extracted, "finalized": finalized}


@app.on_event("startup")
async def on_startup():
    # start auto-finalizer background task (free-mode)
    loop = asyncio.get_event_loop()
    global _finalizer_stop, _finalizer_task
    _finalizer_stop, _finalizer_task = start_background_loop(loop)


@app.on_event("shutdown")
async def on_shutdown():
    global _finalizer_stop, _finalizer_task
    if _finalizer_stop and _finalizer_task:
        _finalizer_stop.set()
        await _finalizer_task

