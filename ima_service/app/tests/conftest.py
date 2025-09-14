"""Ensure the repository root is on sys.path
so `import ima_service` works
"""

import sys
from pathlib import Path

# This file lives at: <repo>/ima_service/app/tests/conftest.py
# repo root = parents[3] (tests -> app -> ima_service -> <repo>)
REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))
