# FILE: main.py
"""
Tiny launcher for any ASGI service.

Usage
-----
  # Typical (from repo root)
  python main.py --service ima_service.app --factory create_app --host 0.0.0.0 --port 8000

Notes
-----
- `--service` is the package path *prefix* (defaults to `ima_service.app`).
- `--factory` is the callable in `<service>.main` that returns an ASGI app
  (defaults to `create_app`). If you prefer a direct app variable, use
  `--factory app`.
- `--env-file` sets ENV_FILE for Pydantic settings resolution before import.
"""

from __future__ import annotations

import os
from argparse import ArgumentParser
from importlib import import_module
from typing import Any, Callable, Protocol, runtime_checkable

import uvicorn


@runtime_checkable
class ASGIApp(Protocol):  # pylint: disable=too-few-public-methods
    """Minimal ASGI application protocol (__call__ only)."""

    def __call__(
        self,
        scope: dict[str, Any],
        receive: Callable[..., Any],
        send: Callable[..., Any],
    ) -> Any:
        """ASGI callable signature: (scope, receive, send) -> awaitable or None."""


def _load_app(service_pkg: str, factory_name: str) -> ASGIApp:
    """
    Import `<service_pkg>.main:<factory_name>` and return the ASGI app.

    - If `factory_name` is a callable, it will be invoked without args.
    - If it's an ASGI app object, it will be returned as-is.
    """
    mod = import_module(f"{service_pkg}.main")
    attr = getattr(mod, factory_name, None)
    if attr is None:
        raise RuntimeError(
            f"Factory or app '{factory_name}' not found in {service_pkg}.main"
        )

    app = attr() if callable(attr) else attr  # create_app() or `app`
    if not isinstance(app, ASGIApp):
        # Best-effort duck-typing check failed
        raise TypeError(
            f"{factory_name} did not produce an ASGI app. "
            "Ensure it returns a FastAPI/Starlette application or expose 'app'."
        )
    return app


def main() -> None:
    """Parse CLI args, load the target ASGI app, and run Uvicorn."""
    parser = ArgumentParser()
    parser.add_argument("--service", default="ima_service.app")
    parser.add_argument("--factory", default="create_app")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--reload", action="store_true")
    parser.add_argument(
        "--env-file",
        default=os.environ.get("ENV_FILE", ""),
        help="Path to .env used by Pydantic settings (sets ENV_FILE).",
    )
    args = parser.parse_args()

    # Ensure ENV_FILE is visible to settings before module import
    if args.env_file:
        os.environ["ENV_FILE"] = args.env_file

    app = _load_app(args.service, args.factory)

    uvicorn.run(
        app,
        host=args.host,
        port=args.port,
        reload=args.reload,
        proxy_headers=True,
        forwarded_allow_ips="*",
        workers=1,
    )


if __name__ == "__main__":
    main()
