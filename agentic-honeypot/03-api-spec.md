# 03 — API Spec

## Authentication
- Header: `x-api-key: YOUR_SECRET_API_KEY`
- Content-Type: `application/json`

## Endpoint
- `POST /events`
- Description: Ingest one incoming message event for a session.

## Request Body (First message)
```json
{
  "sessionId": "wertyu-dfghj-ertyui",
  "message": {
    "sender": "scammer",
    "text": "Your bank account will be blocked today. Verify immediately.",
    "timestamp": "2026-01-21T10:15:30Z"
  },
  "conversationHistory": [],
  "metadata": {
    "channel": "SMS",
    "language": "English",
    "locale": "IN"
  }
}
```

## Response (success)
```json
{
  "status": "success",
  "scamDetected": true,
  "engagementMetrics": {
    "engagementDurationSeconds": 420,
    "totalMessagesExchanged": 18
  },
  "extractedIntelligence": {
    "bankAccounts": ["XXXX-XXXX-XXXX"],
    "upiIds": ["scammer@upi"],
    "phishingLinks": ["http://malicious-link.example"]
  },
  "agentNotes": "Scammer used urgency tactics and payment redirection"
}
```

## Error Codes
- `401` Unauthorized — missing/invalid `x-api-key`
- `400` Bad Request — malformed JSON or missing required fields
- `429` Too Many Requests — rate limit exceeded
- `500` Internal Server Error — retryable

## Callback to GUVI
- POST `https://hackathon.guvi.in/api/updateHoneyPotFinalResult` after finalization.
- Payload fields: `sessionId`, `scamDetected`, `totalMessagesExchanged`, `extractedIntelligence`, `agentNotes`.

## Notes
- Requests representing follow-ups MUST include `conversationHistory`.
- Server should support idempotency for duplicate events (use `sessionId` + message timestamp).