import os
import asyncio
import httpx
from typing import Dict, Any

GUVI_CALLBACK_URL = os.getenv("GUVI_CALLBACK_URL", "https://hackathon.guvi.in/api/updateHoneyPotFinalResult")
CALLBACK_TIMEOUT = float(os.getenv("CALLBACK_TIMEOUT", "5"))


async def send_final_callback(payload: Dict[str, Any], max_retries: int = 3) -> Dict[str, Any]:
    attempt = 0
    backoff = 1.0
    last_exc = None
    async with httpx.AsyncClient(timeout=CALLBACK_TIMEOUT) as client:
        while attempt < max_retries:
            try:
                resp = await client.post(GUVI_CALLBACK_URL, json=payload)
                if resp.status_code >= 200 and resp.status_code < 300:
                    return {"status": "sent", "status_code": resp.status_code, "response": resp.text}
                else:
                    last_exc = Exception(f"Unexpected status {resp.status_code}")
            except Exception as e:
                last_exc = e
            attempt += 1
            await asyncio.sleep(backoff)
            backoff *= 2
    return {"status": "failed", "error": str(last_exc)}
