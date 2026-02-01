# Key Rotation

This document explains how to rotate API keys safely for running backend instances.

1. Use the admin endpoint `POST /admin/rotate-keys` exposed by the backend.
2. Provide a currently valid `x-api-key` in the header to authenticate the request.
3. Body: `{ "keys": ["newkey1","newkey2"] }`.

Example using the provided CLI:

```bash
python scripts/rotate_keys.py --url http://127.0.0.1:8000 --admin-key currentKey newKeyA newKeyB
```

Notes:

- This updates in-process memory and the process-level `API_KEYS` env var. If you use external process managers (systemd, Docker, or Render), also update the environment variable there for future restarts.
- For production, coordinate a rolling key rotation across instances: add new keys first, then remove old keys after traffic is confirmed.
