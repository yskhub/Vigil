# Phase 03 — Testing & CI Walkthrough

Status: Planned

Goals:
- Add unit tests for detector and extractor.
- Add integration tests for `POST /events`.
- Add GitHub Actions workflow for linting, tests, and build.

Planned steps:
1. Add `pytest` and test files under `tests/`.
2. Create `.github/workflows/ci.yml` to run tests and build Docker image.
3. Validate extraction edge-cases and timezone handling.

Acceptance criteria:
- CI passes on push and PRs.
- Tests cover extraction regex and main endpoint responses.