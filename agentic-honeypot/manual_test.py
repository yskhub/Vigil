import requests
import json

url = "http://localhost:8000/events"
headers = {
    "x-api-key": "secret-key",
    "Content-Type": "application/json"
}
payload = {
    "sessionId": "test-session-manual-1",
    "message": {
        "sender": "scammer",
        "text": "URGENT: Your account is blocked. Verify at http://fake-bank.com/login immediately."
    },
    "conversationHistory": [],
    "metadata": {
        "channel": "SMS"
    }
}

try:
    print(f"Sending request to {url}...")
    response = requests.post(url, headers=headers, json=payload)
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        print("Response JSON:")
        print(json.dumps(response.json(), indent=2))
    else:
        print(f"Error: {response.text}")
except Exception as e:
    print(f"Request failed: {e}")
