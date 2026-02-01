# Grafana / Alerts Example

This file contains example ideas for Grafana dashboards and Prometheus alert rules to pair with the `/metrics` endpoint.

Prometheus alert rule example (alert if error rate high):

```yaml
groups:
  - name: honeypot.rules
    rules:
      - alert: HoneypotHighErrorRate
        expr: rate(honeypot_requests_total{status!~"2.."}[5m]) > 0.05
        for: 5m
        labels:
          severity: page
        annotations:
          summary: "High error rate on Agentic HoneyPot"
          description: "{{ $labels.instance }} has >5% errors over 5m"
```

Dashboard suggestions:
- Top-left: sessions throughput (requests/sec)
- Center: ML confidence histogram (custom metric if added)
- Right: Recent error logs (log panel)
