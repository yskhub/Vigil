import requests

url = "http://localhost:8000/events"
headers = {"x-api-key": "secret-key", "Content-Type": "application/json"}
payload = {
    "sessionId": "compliance-test-1",
    "message": {"sender": "scammer", "text": "URGENT ALERT: Your account is blocked. Verify immediately."},
    "conversationHistory": [],
    "metadata": {"channel": "SMS"}
}

try:
    resp = requests.post(url, headers=headers, json=payload)
    data = resp.json()
    
    print(f"Scam Detected: {data.get('scamDetected')}")
    
    intel = data.get("extractedIntelligence", {})
    keywords = intel.get("suspiciousKeywords", [])
    print(f"Suspicious Keywords Found: {keywords}")
    
    reply = data.get("agentReply", {})
    print(f"Agent Reply Text: {reply.get('text')}")
    
    # Validation
    if data.get('scamDetected') is True and "urgent" in keywords and reply.get('text'):
        print("\n✅ COMPLIANCE CHECK PASSED")
    else:
        print("\n❌ COMPLIANCE CHECK FAILED")

except Exception as e:
    print(e)
