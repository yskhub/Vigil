# Redis for local development and CI

This project can use Redis for session storage. To run Redis locally:

```bash
# from repository root
docker-compose up -d redis
```

The app reads `REDIS_URL` environment variable. Example:

```bash
export REDIS_URL=redis://127.0.0.1:6379/0
# on Windows PowerShell
$env:REDIS_URL = 'redis://127.0.0.1:6379/0'
```

CI: GitHub Actions workflow `e2e-tests.yml` now starts a Redis service and sets `REDIS_URL`.
