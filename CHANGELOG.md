# Changelog

All notable changes to this project will be documented in this file.

## Unreleased (2026-01-27)

- Make `src` a package and convert imports to package-relative (commit cdb5973).
- Update tests to import `src.main` to fix collection in package context (commit 03ddaf2).
- Add `.gitignore` to ignore `__pycache__/` and `*.pyc` (commits 2b50edd, 0867a09).
- Remove tracked bytecode files (cleanup) (commit 0867a09).

Notes:
- Package-level tests: 3 passed, 4 warnings (local run).
- Root-level tests require a running server; CI should start `uvicorn` then run root tests.
