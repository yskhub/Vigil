# Runtime Runbook (On-call)

This runbook describes steps to follow when critical alerts fire for the Agentic HoneyPot service.

1) Alert: High error rate or 5xxs
- Check `/metrics` and recent error counts.
- Query the last 30 minutes of `honeypot_requests_total` with `status` != 2xx.
- If errors are due to downstream (Redis) failures, check readiness `/ready` and Redis host connectivity.
- If errors persist, scale replicas or restart the service.

2) Alert: Callback failures to GUVI endpoint
- Inspect logs for `send_final_callback` failures.
- Retry sending payloads from failed callback queue (if any). The system retries with exponential backoff; check logs to see attempts.

3) Alert: Secret compromise suspected
- Immediately rotate API keys using `scripts/rotate_keys.py` with a valid admin key and deploy rotated keys to all instances.
- Revoke any leaked token in cloud provider and rotate secrets in repo/provider.

4) Deploy rollback
- If a deploy caused regression, trigger Render redeploy of the previous successful build or use the docker image tag known-good.

5) Post-mortem
- Create an incident issue with timeline, root cause, actions taken, and remediation steps.

Contacts
- Primary on-call: repo maintainers (add names/emails)
