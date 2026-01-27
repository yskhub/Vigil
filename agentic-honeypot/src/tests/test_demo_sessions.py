import sys
import pathlib
import pytest
import httpx
from httpx import ASGITransport

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from main import app
import main as main_module


@pytest.mark.asyncio
async def test_multi_turn_aggregation_and_finalize(monkeypatch):
    # prepare monkeypatch for callback
    async def fake_send(payload):
        return {"status": "sent", "status_code": 200, "payload": payload}

    monkeypatch.setattr(main_module, "send_final_callback", fake_send)

    transport = ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        session_id = "demo-multi-1"
        payload1 = {
            "sessionId": session_id,
            "message": {"sender": "scammer", "text": "Please share your UPI ID scammer@upi", "timestamp": "2026-01-21T10:15:30Z"},
            "conversationHistory": [],
            "metadata": {"channel": "SMS"}
        }
        r1 = await client.post("/events", json=payload1, headers={"x-api-key": "secret-key"})
        assert r1.status_code == 200

        payload2 = {
            "sessionId": session_id,
            "message": {"sender": "scammer", "text": "Call me at +911234567890 or visit http://bad.example", "timestamp": "2026-01-21T10:16:30Z"},
            "conversationHistory": [ {"sender":"scammer","text":"Please share your UPI ID scammer@upi","timestamp":"2026-01-21T10:15:30Z"} ],
            "metadata": {"channel": "SMS"}
        }
        r2 = await client.post("/events", json=payload2, headers={"x-api-key": "secret-key"})
        assert r2.status_code == 200
        j2 = r2.json()
        # ensure aggregated extraction contains upi, phone, and url
        ei = j2.get("extractedIntelligence", {})
        assert "scammer@upi" in ei.get("upiIds", [])
        assert any("911234567890" in p or "+911234567890" in p for p in ei.get("phoneNumbers", []))
        assert any("bad.example" in u for u in ei.get("phishingLinks", []))

        # now finalize via endpoint and ensure our fake_send was used
        body = {"scamDetected": True, "totalMessagesExchanged": 2, "agentNotes": "demo"}
        rf = await client.post(f"/sessions/{session_id}/finalize", json=body, headers={"x-api-key": "secret-key"})
        assert rf.status_code == 200
        assert rf.json()["result"]["status"] == "sent"
