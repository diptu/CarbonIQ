# main.py
"""
Tiny launcher for any ASGI service.

Usage
-----
  python main.py --service ima_service.app --factory create_app \
    --host 0.0.0.0 --port 8000

Notes
-----
- --service is the package path *prefix* (default: ima_service.app).
- --factory is the callable in `<service>.main` that returns an ASGI app
  (default: create_app). To use a module-level app variable, pass `app`.
- --env-file sets ENV_FILE for Pydantic before import.
"""

from __future__ import annotations

import os
from argparse import ArgumentParser
from importlib import import_module
from typing import Any, Awaitable, Callable, Protocol, runtime_checkable

import uvicorn


@runtime_checkable
class ASGIApp(Protocol):  # pylint: disable=too-few-public-methods
    """Minimal ASGI application protocol."""

    def __call__(
        self,
        scope: dict[str, Any],
        receive: Callable[[], Awaitable[dict[str, Any]]],
        send: Callable[[dict[str, Any]], Awaitable[None]],
    ) -> Any:
        """ASGI signature."""


def _load_app(service_pkg: str, factory_name: str) -> ASGIApp:
    """
    Import `<service_pkg>.main:<factory_name>` and return the ASGI app.

    - If `factory_name` is callable, it will be invoked without args.
    - If it's an ASGI app object, it will be returned as-is.
    """
    try:
        mod = import_module(f"{service_pkg}.main")
    except Exception as exc:  # pylint: disable=broad-except
        raise RuntimeError(f"Could not import module '{service_pkg}.main'.") from exc

    if not hasattr(mod, factory_name):
        raise RuntimeError(
            f"Factory or app '{factory_name}' not found in {service_pkg}.main"
        )

    attr = getattr(mod, factory_name)
    app = attr() if callable(attr) else attr
    if not isinstance(app, ASGIApp):
        raise TypeError(
            f"'{factory_name}' did not produce an ASGI app. Return a "
            "FastAPI/Starlette app or expose an 'app' variable."
        )
    return app


def main() -> None:
    """Parse args, load ASGI app, and run Uvicorn."""
    parser = ArgumentParser()
    parser.add_argument("--service", default="ima_service.app")
    parser.add_argument("--factory", default="create_app")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--reload", action="store_true")
    parser.add_argument(
        "--log-level",
        default=os.environ.get("LOG_LEVEL", "info"),
        choices=["critical", "error", "warning", "info", "debug", "trace"],
    )
    parser.add_argument(
        "--env-file",
        default=os.environ.get("ENV_FILE", ""),
        help="Path to .env used by settings (sets ENV_FILE).",
    )
    args = parser.parse_args()

    if args.port < 0 or args.port > 65535:
        raise ValueError("Port must be in 0..65535.")

    # Ensure ENV_FILE is visible to settings before module import.
    if args.env_file:
        os.environ["ENV_FILE"] = args.env_file

    app = _load_app(args.service, args.factory)

    uvicorn.run(
        app,
        host=args.host,
        port=args.port,
        reload=args.reload,
        log_level=args.log_level,  # integrates with your core logging level
        proxy_headers=True,
        forwarded_allow_ips="*",
        workers=1,
    )


if __name__ == "__main__":
    main()
