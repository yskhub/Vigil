# PR Review Checklist

Use this checklist to validate PR readiness before merging.

- [ ] Code compiles / lints with project settings
- [ ] Unit tests pass locally and in CI
- [ ] Integration / end-to-end tests (if any) ran and passed
- [ ] No secrets or credentials committed
- [ ] `requirements-dev.txt` and other dependency files updated if needed
- [ ] Documentation updated (`CHANGELOG.md`, `README.md`, `docs/`)
- [ ] Migration or lifecycle changes documented and tested (e.g., FastAPI lifespan)
- [ ] Dockerfile / render.yaml updated (if deployment changes)
- [ ] Security review: auth, rate-limits, input validation checked
- [ ] Performance review: critical paths reviewed for latency (detection path)
- [ ] CI workflow configured to install dev deps and run tests (see `.github/workflows/ci.yml`)
- [ ] Reviewer assigned and at least one approval obtained
- [ ] Merge strategy decided (squash/merge, rebase) and commit message updated

Post-merge tasks:
- [ ] Deploy to staging and verify health endpoints
- [ ] Rotate any exposed keys and confirm env propagation
- [ ] Monitor logs and rollback plan ready

Add any repository-specific checks below.
