from fastapi import FastAPI, Header, HTTPException, Request
from starlette.responses import JSONResponse
from starlette.requests import Request as StarletteRequest
from starlette.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
import os
import json
import re
import asyncio
from contextlib import asynccontextmanager

from .session_store import SessionStore
from .agent import AgentOrchestrator
from .callback_worker import send_final_callback
from .auto_finalizer import start_background_loop
from .auth import check_api_key, rate_limit_ok
from .auth import set_api_keys
from prometheus_client import make_asgi_app, Counter, Summary
import time
import logging

# configure structured logging
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)
logger = logging.getLogger("agentic-honeypot")


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

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Prometheus metrics
REQUESTS = Counter("honeypot_requests_total", "Total requests", ["endpoint", "method", "status"])
LATENCY = Summary("honeypot_request_latency_seconds", "Request latency in seconds")

# mount metrics endpoint
app.mount("/metrics", make_asgi_app())


@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    start = time.perf_counter()
    try:
        resp = await call_next(request)
        status = str(resp.status_code)
    except Exception:
        status = "500"
        raise
    finally:
        elapsed = time.perf_counter() - start
        LATENCY.observe(elapsed)
        REQUESTS.labels(endpoint=request.url.path, method=request.method, status=status).inc()
    return resp

API_KEY = os.getenv("BACKEND_API_KEY", os.getenv("API_KEY", "default-dev-key"))
API_KEYS = None

# init services
session_store = SessionStore()
agent = AgentOrchestrator()

# Request models
class Message(BaseModel):
    # Completely relaxed for debugging
    sender: Optional[Any] = "unknown"
    text: Optional[Any] = ""
    timestamp: Optional[Any] = None

class Event(BaseModel):
    sessionId: str
    message: Union[Message, Dict[str, Any]]
    conversationHistory: Optional[List[Dict[str, Any]]] = None
    metadata: Optional[Dict[str, Any]] = None

# Custom Validation Error Handler
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    import logging
    logger = logging.getLogger("agentic-honeypot")
    body = await request.body()
    logger.error(f"Validation Error: {exc.errors()} | Body: {body.decode('utf-8')}")
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors(), "body": body.decode('utf-8')},
    )


class RotateKeysBody(BaseModel):
    keys: List[str]


# Simple rule-based detector
SCAM_KEYWORDS = [
    "verify", "account blocked", "will be blocked", "upi id", "share your", "bank account",
    "suspend", "suspension", "immediately", "urgent", "verify now", "password",
]

UPI_RE = re.compile(r"\b[\w.-]{2,}@[a-zA-Z]{2,}\b")
PHONE_RE = re.compile(r"(?:\+?\d{1,3}[\s-]?)?(?:\d{10}|\d{3}[\s-]\d{3}[\s-]\d{4})")
URL_RE = re.compile(r"https?://[\w./?=&%-]+|www\.[\w./?=&%-]+")
ACC_RE = re.compile(r"\b\d{6,20}\b")


def normalize_timestamp(ts: Union[datetime, int, float, str, None]) -> datetime:
    if ts is None:
        return datetime.utcnow()
    if isinstance(ts, datetime):
        return ts
    if isinstance(ts, str):
        try:
            return datetime.fromisoformat(ts.replace("Z", "+00:00"))
        except:
            return datetime.utcnow()
    if isinstance(ts, (int, float)):
        # If > 1e11 (100 billion), assume milliseconds (Year 1973+)
        if ts > 1e11:
            ts = ts / 1000.0
        try:
            return datetime.utcfromtimestamp(ts)
        except (ValueError, OSError):
            return datetime.utcnow()
    return datetime.utcnow()


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
    
    # Extract suspicious keywords from the text as well
    matched_keywords = [k for k in SCAM_KEYWORDS if k in text.lower()]
    
    return {
        "bankAccounts": accounts,
        "upiIds": upis,
        "phishingLinks": urls,
        "phoneNumbers": phones,
        "suspiciousKeywords": matched_keywords,
    }


@app.post("/events", include_in_schema=False)
async def handle_event_wrapper(request: Request):
    """
    Wrapper to manually handle the request and ensure we catch EVERYTHING
    before FastAPI validation kicks in.
    """
    # Raw header check
    x_api_key = request.headers.get("x-api-key")
    if not x_api_key or not check_api_key(x_api_key):
        # Return 401 manually
        return JSONResponse({"detail": "Unauthorized: invalid x-api-key"}, status_code=401)
        
    try:
        body_bytes = await request.body()
        if not body_bytes:
            body = {}
        else:
            try:
                body = json.loads(body_bytes)
            except:
                body = {}
    except:
        body = {}

    print(f"DEBUG INCOMING BODY: {body}")
    
    # Delegate to internal logic
    return await process_event_logic(body)

async def process_event_logic(body: Dict[str, Any]):
    # Manual Extraction
    event_id = body.get("sessionId", "unknown_session")
    msg_obj = body.get("message", {})
    if not isinstance(msg_obj, dict):
        msg_obj = {"text": str(msg_obj), "sender": "unknown"}
    
    msg_sender = str(msg_obj.get("sender") or "unknown")
    msg_text = str(msg_obj.get("text") or "")
    msg_ts = msg_obj.get("timestamp")
    if not rate_limit_ok(x_api_key):
        raise HTTPException(status_code=429, detail="Rate limit exceeded")

    # Ensure incoming message has a timestamp; default to now if missing/empty
    # Ensure incoming message has a timestamp (handle int/float ms or s)
    final_ts = normalize_timestamp(msg_ts)

    # Safe defaults for optional fields
    conv_history = body.get("conversationHistory") or []
    if not isinstance(conv_history, list): conv_history = []
    
    meta = body.get("metadata") or {}
    if not isinstance(meta, dict): meta = {}

    # Combine latest message + conversation history for extraction
    all_texts = []
    for msg in conv_history:
        txt = msg.get("text") if isinstance(msg, dict) else None
        if txt:
            all_texts.append(txt)
    all_texts.append(msg_text)
    full_text = "\n".join(all_texts)

    # Ensure defaults
    if not msg_sender:
        msg_sender = "unknown"
    if not msg_text:
        msg_text = "..."

    detection = detect_scam(msg_text)
    extracted = extract_from_text(full_text)

    # Persist incoming message to session store
    await session_store.append_message(event_id, {"sender": msg_sender, "text": msg_text, "timestamp": final_ts.isoformat()})
    # Merge any existing extracted intelligence
    prev_extracted = await session_store.get_extracted(event_id)
    merged = {}
    for k in set(list(prev_extracted.keys()) + list(extracted.keys())):
        prev_list = prev_extracted.get(k, []) or []
        new_list = extracted.get(k, []) or []
        merged[k] = list(dict.fromkeys(prev_list + new_list))
    await session_store.set_extracted(event_id, merged)

    # Basic engagement metrics (prototype)
    total_messages = len(conv_history) + 1
    engagement_seconds = 0
    try:
        timestamps = []
        for m in conv_history:
            try:
                t = m.get("timestamp")
                if t:
                    timestamps.append(normalize_timestamp(t))
            except:
                pass
        timestamps.append(final_ts)
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
        local_history = await session_store.get_history(event_id)
        
        # If local history is empty but we have provided history, hydrate it for context
        if not local_history and conv_history:
             local_history = conv_history

        # Check if latest user message is already in history (idempotency check roughly)
        if len(local_history) == 1 and local_history[0].get("text") == msg_text and conv_history:
             # Prepend the provided history
             full_history = conv_history + local_history
        else:
             full_history = local_history

        # Fallback if somehow empty
        if not full_history:
             full_history = [{"sender": msg_sender, "text": msg_text, "timestamp": final_ts.isoformat()}]

        agent_reply = await agent.generate_reply(event_id, full_history, meta)
        # persist agent reply
        await session_store.append_message(event_id, agent_reply)

    response_data = {
        "status": "success",
        "reply": agent_reply["text"] if agent_reply else "No conversation started.",
        "scamDetected": detection["scam"],
        "engagementMetrics": {
            "engagementDurationSeconds": engagement_seconds,
            "totalMessagesExchanged": total_messages,
        },
        "extractedIntelligence": merged,
        "agentNotes": " ".join(agent_notes) if agent_notes else "No flags detected.",
    }

    if agent_reply:
        response_data["agentReply"] = agent_reply

    return JSONResponse(response_data)


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/ready")
async def readiness_check():
    """Readiness probe: returns 200 if core dependencies are available.

    Checks Redis connectivity if the session store was configured to use Redis.
    """
    redis_status = True
    try:
        use_redis = getattr(session_store, "_use_redis", False)
        if use_redis:
            r = getattr(session_store, "_r", None)
            if r is None:
                redis_status = False
            else:
                try:
                    pong = await r.ping()
                    redis_status = bool(pong)
                except Exception:
                    redis_status = False
    except Exception:
        redis_status = False

    if not redis_status:
        return {"status": "not ready", "redis": False}
    return {"status": "ready", "redis": True}


@app.post("/admin/rotate-keys")
async def rotate_keys(body: RotateKeysBody, x_api_key: Optional[str] = Header(None)):
    # Only allow if caller presents a valid API key
    if x_api_key is None or not check_api_key(x_api_key):
        raise HTTPException(status_code=401, detail="Unauthorized: invalid x-api-key")
    ok = set_api_keys(body.keys)
    if not ok:
        raise HTTPException(status_code=500, detail="Failed to set keys")
    return {"status": "ok", "keys_count": len(body.keys)}


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


# Lifespan handler above already starts and stops the auto-finalizer.
# The older `@app.on_event` startup/shutdown handlers were removed to
# avoid DeprecationWarning and to consolidate lifecycle management
# via the `lifespan` async context manager defined at the top of this
# module.

