import asyncio
import os
from typing import Any
from .session_store import SessionStore
from .callback_worker import send_final_callback

POLL_INTERVAL = float(os.getenv("AUTO_FINALIZE_POLL_INTERVAL", "10"))
MIN_MESSAGES_TO_FINALIZE = int(os.getenv("MIN_MESSAGES_TO_FINALIZE", "5"))
IDLE_SECONDS_TO_FINALIZE = int(os.getenv("IDLE_SECONDS_TO_FINALIZE", "300"))

session_store = SessionStore()


async def evaluate_and_finalize():
    sessions = await session_store.list_sessions()
    for s in sessions:
        try:
            if await session_store.is_finalized(s):
                continue
            extracted = await session_store.get_extracted(s)
            if any(extracted.get(k) for k in ["bankAccounts", "upiIds", "phishingLinks", "phoneNumbers"]):
                # enough intelligence
                payload = {
                    "sessionId": s,
                    "scamDetected": True,
                    "totalMessagesExchanged": await session_store.get_total_messages(s),
                    "extractedIntelligence": extracted,
                    "agentNotes": "Auto-finalized by heuristic: extracted items found",
                }
                result = await send_final_callback(payload)
                if result.get("status") == "sent":
                    await session_store.mark_finalized(s)
                continue

            total = await session_store.get_total_messages(s)
            if total >= MIN_MESSAGES_TO_FINALIZE:
                payload = {
                    "sessionId": s,
                    "scamDetected": True,
                    "totalMessagesExchanged": total,
                    "extractedIntelligence": extracted,
                    "agentNotes": "Auto-finalized by heuristic: message count threshold",
                }
                result = await send_final_callback(payload)
                if result.get("status") == "sent":
                    await session_store.mark_finalized(s)
                continue

            last_seen = await session_store.get_last_seen(s)
            import time
            if last_seen and (time.time() - last_seen) >= IDLE_SECONDS_TO_FINALIZE:
                payload = {
                    "sessionId": s,
                    "scamDetected": True,
                    "totalMessagesExchanged": total,
                    "extractedIntelligence": extracted,
                    "agentNotes": "Auto-finalized by heuristic: idle timeout",
                }
                result = await send_final_callback(payload)
                if result.get("status") == "sent":
                    await session_store.mark_finalized(s)
                continue
        except Exception:
            # swallow per-session errors
            continue


async def _run_loop(stop_event: asyncio.Event):
    while not stop_event.is_set():
        try:
            await evaluate_and_finalize()
        except Exception:
            pass
        try:
            await asyncio.wait_for(stop_event.wait(), timeout=POLL_INTERVAL)
            break  # stop_event was set
        except asyncio.TimeoutError:
            continue  # timeout reached, continue loop


def start_background_loop(loop):
    stop_event = asyncio.Event()
    task = loop.create_task(_run_loop(stop_event))
    return stop_event, task
