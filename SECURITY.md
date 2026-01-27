# Security Checklist

Minimum checks performed in CI:

- Secret scanning: `gitleaks` runs in CI to detect leaked secrets.
- Static security scan: `bandit` is run against Python code to flag common issues.

Before public deploy:

1. Rotate any keys that were committed in the past.
2. Ensure `.env` is in `.gitignore` and `.env.example` is present with placeholders.
3. Review `SECURITY.md` and `docs/key_rotation.md` for responsible rotation steps.
4. Add runtime secrets to your cloud provider's secret store (Render/Heroku/GCP Secret Manager).
5. Limit `BACKEND_API_KEY` scope and rotate after major changes.

Reporting:
- If you find a security issue, open a private issue and tag maintainers.
