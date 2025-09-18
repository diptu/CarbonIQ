"""
Ensure the repository root is on sys.path
so `import ima_service` works in tests.
"""

from __future__ import annotations

import sys
from pathlib import Path

# This file lives at: <repo>/ima_service/app/tests/conftest.py
# Step up three levels to reach the repo root.
_REPO_ROOT = Path(__file__).resolve().parents[3]

if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
