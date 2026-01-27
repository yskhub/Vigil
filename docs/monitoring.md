# Monitoring and Metrics

This project exposes Prometheus-compatible metrics at `/metrics` and includes basic request counters and latency summaries.

Quick checks:

- Metrics URL (local): `http://127.0.0.1:8000/metrics`
- Example: curl -s http://127.0.0.1:8000/metrics

Prometheus scrape config snippet:

```yaml
scrape_configs:
  - job_name: 'agentic-honeypot'
    static_configs:
      - targets: ['YOUR_HOST:8000']
    metrics_path: /metrics
```

Admin endpoints:

- Rotate API keys (protected): `POST /admin/rotate-keys` with JSON `{ "keys": ["key1","key2"] }` and `x-api-key` header of a currently valid key.

Notes:

- Metrics are provided via `prometheus_client`'s ASGI app and a small middleware that records request counts and latency.
- For production, run a Prometheus instance pointing to `/metrics` and use Grafana for dashboards.
