Security notes — minimal free-mode protections

- API keys: Configure `API_KEYS` environment variable with comma-separated API keys. Default is `API_KEY` value `secret-key`.
- Rate limiting: Basic in-memory per-key rate limit controlled by `RATE_LIMIT_PER_MIN` (default 60).
- For production: replace in-memory stores with Redis or managed secrets, implement stronger auth (JWT or OAuth), and use HTTPS.

To change keys and limits, set env vars in your deployment environment.
