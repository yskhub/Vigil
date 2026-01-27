import requests
import os
from datetime import datetime

API_URL = os.getenv("API_URL", "http://localhost:8000/events")
API_KEY = os.getenv("API_KEY", "secret-key")

payload = {
    "sessionId": "test-session-1",
    "message": {
        "sender": "scammer",
        "text": "Your bank account will be blocked today. Verify immediately. Share your UPI ID.",
        "timestamp": datetime.utcnow().isoformat()
    },
    "conversationHistory": [],
    "metadata": {"channel": "SMS", "language": "English", "locale": "IN"}
}

headers = {"Content-Type": "application/json", "x-api-key": API_KEY}

r = requests.post(API_URL, json=payload, headers=headers, timeout=5)
print("status", r.status_code)
print(r.json())
