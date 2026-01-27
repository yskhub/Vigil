import os
import asyncio
import httpx
from src.main import app

API_KEY = os.getenv("API_KEY", "secret-key")


async def test_simple_event():
    payload = {
        "sessionId": "local-test-1",
        "message": {
            "sender": "scammer",
            "text": "Your bank account will be blocked today. Verify immediately. Share your UPI ID: scammer@upi",
            "timestamp": "2026-01-21T10:15:30Z"
        },
        "conversationHistory": [],
        "metadata": {"channel": "SMS", "language": "English", "locale": "IN"}
    }
    headers = {"x-api-key": API_KEY}
    from httpx import ASGITransport
    transport = ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        r = await client.post("/events", json=payload, headers=headers)
        print("status", r.status_code)
        try:
            print(r.json())
        except Exception:
            print(r.text)


if __name__ == '__main__':
    asyncio.run(test_simple_event())
