# ima_service/main.py
"""
ima_service entrypoint.

This makes the service runnable directly:
  uv run python -m ima_service.main
"""

import uvicorn
from ima_service.app.server import app


if __name__ == "__main__":
    uvicorn.run("ima_service.app.main:app", host="127.0.0.1", port=8000, reload=True)
