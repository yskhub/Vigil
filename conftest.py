import os
import sys

# Ensure the test environment can import the `src` package located under
# the `agentic-honeypot` folder when pytest is run from the repository root.
ROOT = os.path.dirname(__file__)
AGENTIC_DIR = os.path.join(ROOT, "agentic-honeypot")
if os.path.isdir(AGENTIC_DIR) and AGENTIC_DIR not in sys.path:
    sys.path.insert(0, AGENTIC_DIR)
