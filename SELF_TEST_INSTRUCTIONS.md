# Self-Testing Guide: Before You Submit to Judges

Follow these steps exactly to verify your system is ready.

## 🔑 Your Credentials
*   **API Endpoint**: `https://vigil-889d.onrender.com/events`
*   **API Key**: `Agentic_Honey_Pot_Scam_Detection_Intelligence_Extraction_2026_X1`

---

## 🟢 Test 1: Verify "First Submission" Readiness
**Goal**: Ensure your API is live, accepts your Key, and allows the Judge's tester to connect.

**Action**: Open `PowerShell` and run this command block:

```powershell
$url = "https://vigil-889d.onrender.com/events"
$key = "Agentic_Honey_Pot_Scam_Detection_Intelligence_Extraction_2026_X1"

# Mimic the Judge's "Ping" or Simple Message
$body = @{
    sessionId = "test-submission-1"
    message = @{ sender="user"; text="Hello, just testing connection." }
    conversationHistory = @()
    metadata = @{ channel = "web-tester" }
} | ConvertTo-Json -Depth 5

try {
    $response = Invoke-RestMethod -Uri $url -Method Post -Headers @{"x-api-key"=$key; "Content-Type"="application/json"} -Body $body
    Write-Host "✅ Connection Successful!" -ForegroundColor Green
    Write-Host "Response:"
    $response | ConvertTo-Json
} catch {
    Write-Host "❌ Connection Failed" -ForegroundColor Red
    Write-Host $_.Exception.Message
}
```

**What to verify:**
1.  You see **"✅ Connection Successful!"**.
2.  You get a JSON response (even if `scamDetected` is false, that's fine for a "Hello" message).
3.  **If this passes**: You are 100% safe to do the "First Submission".

---

## 🧠 Test 2: Verify "Final Submission" Logic (The Martha Test)
**Goal**: Ensure your "Martha" persona triggers and Intelligence Extraction works.

**Action**: Run this "Scam Attack" simulation in PowerShell:

```powershell
$url = "https://vigil-889d.onrender.com/events"
$key = "Agentic_Honey_Pot_Scam_Detection_Intelligence_Extraction_2026_X1"

# Mimic a Scammer
$body = @{
    sessionId = "test-final-martha-1"
    message = @{ 
        sender = "scammer"; 
        text = "URGENT WARNING: Your bank account will be suspended. Verify now at http://bad-link.com/login" 
    }
    conversationHistory = @()
    metadata = @{ channel = "SMS" }
} | ConvertTo-Json -Depth 5

$response = Invoke-RestMethod -Uri $url -Method Post -Headers @{"x-api-key"=$key; "Content-Type"="application/json"} -Body $body

Write-Host "--- TEST RESULTS ---"
Write-Host "1. Scam Detected? : " $response.scamDetected
Write-Host "2. Agent Reply    : " $response.agentReply.text
Write-Host "3. Keywords Found : " ($response.extractedIntelligence.suspiciousKeywords -join ", ")
```

**What to verify:**
1.  **Scam Detected**: Must be `True`.
2.  **Agent Reply**: Should be something confused like *"I tried to click the blue thing but nothing happened..."* (Martha's voice).
3.  **Keywords**: Should show `urgent`, `verify`, or similar.

---

## 🕵️ Test 3: Verify the "Callback" (Optional but Recommended)
**Goal**: Check if your server tried to report the result to GUVI.

1.  Run **Test 2** again.
2.  Go to your **Render Dashboard** > **Logs**.
3.  Look for a line that says `Sending final callback for session...`.
    *   *Note: Since this is a test, the GUVI server might reply with an error or success, but the important thing is that YOUR logs show you tried to send it.*

---

## 🚀 Ready?
If Test 1 and Test 2 pass, you are ready to submit!
1.  **First Submission**: Paste URL & Key.
2.  **Final Submission**: Paste URL & Key.
