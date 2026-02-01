# Health & Readiness

Endpoints:

- `/health` — liveness probe (returns 200 when the app process is alive).
- `/ready` — readiness probe (returns 200 when core dependencies like Redis are reachable).

Docker:

- The `Dockerfile` contains a `HEALTHCHECK` which hits `/ready`.

Kubernetes probes (example):

```yaml
livenessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 5
  periodSeconds: 10
readinessProbe:
  httpGet:
    path: /ready
    port: 8000
  initialDelaySeconds: 5
  periodSeconds: 10
```
