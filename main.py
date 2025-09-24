# carbon_IQ/main.py
import argparse
import importlib
import sys
import uvicorn


def _load_app(service: str, factory: str | None):
    """
    Dynamically load a FastAPI app instance or a factory function from the given service.
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


def main():
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
        "--log-level",
        type=str,
        default="info",
        choices=["critical", "error", "warning", "info", "debug", "trace"],
        help="Log level",
    )
    args = parser.parse_args()

    if args.reload and not args.factory:
        # Uvicorn reload requires import string (module:variable)
        import_str = f"{args.service}.main:app"
        uvicorn.run(
            import_str,
            host=args.host,
            port=args.port,
            reload=True,
            log_level=args.log_level,
        )
    else:
        # Load app directly (factory or plain app)
        app = _load_app(args.service, args.factory)
        uvicorn.run(
            app,
            host=args.host,
            port=args.port,
            reload=args.reload,
            log_level=args.log_level,
        )


if __name__ == "__main__":
    sys.exit(main())
