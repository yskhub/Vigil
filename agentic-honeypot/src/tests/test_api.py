import os
import sys
import pathlib
import pytest
import httpx
from httpx import ASGITransport

# ensure src directory is importable
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from src.main import app
import src.main as main_module

API_KEY = os.getenv("API_KEY", "secret-key")


async def post_event(payload):
    transport = ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        r = await client.post("/events", json=payload, headers={"x-api-key": API_KEY})
        return r


@pytest.mark.asyncio
async def test_event_detection_and_agent():
    payload = {
        "sessionId": "test-session-async-1",
        "message": {
            "sender": "scammer",
            "text": "Your bank account will be blocked today. Verify immediately. Share your UPI ID: scammer@upi",
            "timestamp": "2026-01-21T10:15:30Z"
        },
        "conversationHistory": [],
        "metadata": {"channel": "SMS", "language": "English", "locale": "IN"}
    }
    r = await post_event(payload)
    assert r.status_code == 200
    j = r.json()
    assert j.get("scamDetected") is True
    assert "scammer@upi" in j.get("extractedIntelligence", {}).get("upiIds", [])
    assert "agentReply" in j


@pytest.mark.asyncio
async def test_finalize_endpoint_calls_callback(monkeypatch):
    async def fake_send(payload):
        return {"status": "sent", "status_code": 200}

    monkeypatch.setattr(main_module, "send_final_callback", fake_send)
    session_id = "test-session-async-1"
    body = {"scamDetected": True, "totalMessagesExchanged": 2, "agentNotes": "note"}
    transport = ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        r = await client.post(f"/sessions/{session_id}/finalize", json=body, headers={"x-api-key": API_KEY})
        assert r.status_code == 200
        j = r.json()
        assert j["status"] == "callback_attempted"
        assert j["result"]["status"] == "sent"
