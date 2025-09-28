# carbon_IQ/main.py
"""
Entry point to run CarbonIQ FastAPI services dynamically.
Supports loading apps directly or via factory functions, with optional auto-reload and debug mode.
"""

import argparse
import importlib
import sys
from typing import Optional, Any

import uvicorn


def _load_app(service: str, factory: Optional[str] = None) -> Any:
    """
    Dynamically load a FastAPI app instance or a factory function from the given service.

    Args:
        service (str): Name of the service module (e.g., 'ima_service').
        factory (Optional[str]): Name of a factory function to create the app.

    Returns:
        Any: Loaded FastAPI app instance.

    Raises:
        RuntimeError: If the app or factory function cannot be found or called.
    """
    module_name = f"{service}.main"
    module = importlib.import_module(module_name)

    if factory:
        obj = getattr(module, factory, None)
        if obj is None or not callable(obj):
            raise RuntimeError(
                f"Factory '{factory}' not found in {module_name}. "
                f"Make sure to define `{factory}` in {module_name}.py"
            )
        return obj()  # Call the factory function
    else:
        app = getattr(module, "app", None)
        if app is None:
            raise RuntimeError(
                f"App instance 'app' not found in {module_name}. "
                f"Define `app = FastAPI()` or use --factory."
            )
        return app


def main() -> None:
    """Parse CLI arguments and run the selected CarbonIQ service via Uvicorn."""
    parser = argparse.ArgumentParser(description="Run CarbonIQ services")
    parser.add_argument(
        "--service", type=str, required=True, help="Service to run (e.g., ima_service)"
    )
    parser.add_argument(
        "--factory",
        type=str,
        default=None,
        help="Factory function to create the app (e.g., create_app)",
    )
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Host to bind")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind")
    parser.add_argument(
        "--reload", action="store_true", help="Enable auto-reload on code changes"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode (debug logging & reload)",
    )
    parser.add_argument(
        "--log-level",
        type=str,
        default="info",
        choices=["critical", "error", "warning", "info", "debug", "trace"],
        help="Log level",
    )
    args = parser.parse_args()

    log_level = "debug" if args.debug else args.log_level
    reload_flag = args.reload or args.debug

    if reload_flag and not args.factory:
        # Uvicorn reload requires import string (module:variable)
        import_str = f"{args.service}.main:app"
        uvicorn.run(
            import_str,
            host=args.host,
            port=args.port,
            reload=True,
            log_level=log_level,
        )
    else:
        # Load app directly (factory or plain app)
        app = _load_app(args.service, args.factory)
        uvicorn.run(
            app,
            host=args.host,
            port=args.port,
            reload=reload_flag,
            log_level=log_level,
        )


if __name__ == "__main__":
    sys.exit(main())
