import os
import pathlib
import sys
import pytest
import httpx
from httpx import ASGITransport

# make src importable when running from repo root
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from src.main import app
import src.main as main_module

API_KEY = os.getenv("API_KEY", "secret-key")


async def post_event(client, payload):
    r = await client.post("/events", json=payload, headers={"x-api-key": API_KEY})
    return r


@pytest.mark.asyncio
async def test_end_to_end_flow(monkeypatch):
    # fake the external callback to avoid network calls
    async def fake_send(payload):
        return {"status": "sent", "status_code": 200}

    monkeypatch.setattr(main_module, "send_final_callback", fake_send)

    transport = ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        # send first scammy message (no timestamp)
        payload1 = {
            "sessionId": "e2e-session-1",
            "message": {"sender": "scammer", "text": "Please verify your UPI scammer@upi now"},
            "conversationHistory": [],
            "metadata": {"channel": "SMS"}
        }
        r1 = await post_event(client, payload1)
        assert r1.status_code == 200
        j1 = r1.json()
        assert j1.get("scamDetected") is True

        # send a follow-up message (simulate conversation)
        payload2 = {
            "sessionId": "e2e-session-1",
            "message": {"sender": "scammer", "text": "Share your account 123456789012 now"},
            "conversationHistory": [
                {"sender": "scammer", "text": payload1["message"]["text"], "timestamp": "2026-01-21T10:15:30Z"}
            ],
            "metadata": {"channel": "SMS"}
        }
        r2 = await post_event(client, payload2)
        assert r2.status_code == 200
        j2 = r2.json()
        # ensure extracted intelligence contains expected types
        ext = j2.get("extractedIntelligence", {})
        assert isinstance(ext, dict)

        # finalize the session
        body = {"scamDetected": True, "totalMessagesExchanged": 2, "agentNotes": "auto"}
        r3 = await client.post(f"/sessions/e2e-session-1/finalize", json=body, headers={"x-api-key": API_KEY})
        assert r3.status_code == 200
        j3 = r3.json()
        assert j3.get("status") == "callback_attempted"
