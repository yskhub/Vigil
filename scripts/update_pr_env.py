import os
import sys
import requests

token = os.getenv("GITHUB_TOKEN")
if not token:
    print("GITHUB_TOKEN not set. Please set the env var and retry.", file=sys.stderr)
    sys.exit(2)

url = "https://api.github.com/repos/yskhub/Vigil/pulls/1"
body_text = '''Packaging & CI fixes

Summary:
- Make `src` a package and convert imports to package-relative.
- Update tests to import `src.main`.
- Add .gitignore to ignore __pycache__/ and remove tracked bytecode.
- Add agentic-honeypot/requirements-dev.txt (includes pytest-asyncio).
- Rename local runnable test helper to avoid pytest collection.
- Migrate startup/shutdown to FastAPI lifespan handler to remove deprecation warnings.
- Add GitHub Actions CI workflow to install dev requirements, start uvicorn, and run pytest.
- Add CHANGELOG.md with details.

Verification:
- Local simulated CI run: server started and tests executed (3 passed, 4 warnings). Package-level tests passed.

Next steps:
- Please review and merge. I can update the PR further or add additional CI checks on request.
'''

headers = {'Authorization': f'token {token}', 'Accept': 'application/vnd.github+json'}
resp = requests.patch(url, headers=headers, json={'body': body_text})
print(resp.status_code)
try:
    j = resp.json()
    print(j.get('html_url'))
    if 'message' in j:
        print('message:', j.get('message'))
except Exception as e:
    print('no json', e)
