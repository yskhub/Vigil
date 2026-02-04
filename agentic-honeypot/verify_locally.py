
import urllib.request
import json
import ssl
import time

# Local Configuration
URL = "http://127.0.0.1:8000/events"
API_KEY = "secret-key" # Default key in auth.py

# Payload exactly from Judges
PAYLOAD = {
    "sessionId": "1fc994e9-f4c5-47ee-8806-90aeb969928f",
    "message": {
        "sender": "scammer",
        "text": "Your bank account will be blocked today. Verify immediately.",
        "timestamp": 1769776085000
    },
    "conversationHistory": [
         {
              "sender": "user",
              "text": "Hello", 
              "timestamp": 1769776085000
         }
    ],
    "metadata": {
        "channel": "SMS",
        "language": "English",
        "locale": "IN"
    }
}

def run_test():
    print(f"--- LOCAL JUDGE COMPLIANCE TEST ---")
    print(f"Target: {URL}")
    print("Sending Judges' Sample Payload...")
    
    req = urllib.request.Request(
        URL,
        data=json.dumps(PAYLOAD).encode('utf-8'),
        headers={
            "Content-Type": "application/json",
            "x-api-key": API_KEY
        },
        method="POST"
    )

    try:
        # No SSL for localhost
        with urllib.request.urlopen(req) as response:
            status = response.status
            body = response.read().decode('utf-8')
            
            print(f"HTTP Status: {status}")
            try:
                data = json.loads(body)
                print("Response JSON:")
                print(json.dumps(data, indent=2))
                
                # Verification logic
                checks = []
                checks.append(("HTTP 200", status == 200))
                checks.append(("'status' is 'success'", data.get("status") == "success"))
                checks.append(("'reply' field exists", "reply" in data))
                checks.append(("'reply' is non-empty string", isinstance(data.get("reply"), str) and len(data["reply"]) > 0));
                
                failed = [name for name, passed in checks if not passed]
                
                if not failed:
                    print("\n✅ PASS: API behaves exactly as Judges expect (Locally).")
                else:
                    print(f"\n❌ FAIL: Failed checks: {', '.join(failed)}")
                    
            except json.JSONDecodeError:
                print(f"❌ FAIL: Invalid JSON response.\nBody: {body}")

    except urllib.request.HTTPError as e:
        print(f"❌ FAIL: HTTP Error {e.code}")
        try:
            print(e.read().decode('utf-8'))
        except:
            pass
    except Exception as e:
        print(f"❌ ERROR: {e}")

if __name__ == "__main__":
    # give server a sec to start
    time.sleep(2)
    run_test()
