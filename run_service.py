# carboniq/run_service.py
"""
Run any CarbonIQ microservice with proper venv activation.

Usage:
    python run_service.py --service ima_service --reload
    python run_service.py --service tenant_service --port 8001
"""

import argparse
import importlib
import os
import sys
import subprocess
from typing import Optional, Any

import uvicorn

# Mapping of service -> its venv path
SERVICE_VENVS = {
    "ima_service": "ima_service/.venv",
    "tenant_service": "tenant_service/.venv",
}


def _activate_venv(venv_path: str):
    """Activate the virtualenv in the current Python process."""
    activate_script = os.path.join(venv_path, "bin", "activate_this.py")
    if os.path.exists(activate_script):
        # Execute the activate_this.py script to patch sys.path & interpreter
        with open(activate_script) as f:
            code = compile(f.read(), activate_script, "exec")
            exec(code, dict(__file__=activate_script))
    else:
        # fallback: prepend venv site-packages to sys.path
        site_packages = os.path.join(
            venv_path,
            "lib",
            f"python{sys.version_info.major}.{sys.version_info.minor}",
            "site-packages",
        )
        if os.path.exists(site_packages):
            sys.path.insert(0, site_packages)


def _setup_path(service: str) -> None:
    """Add project root and service root to sys.path for imports."""
    project_root = os.path.dirname(os.path.abspath(__file__))
    service_root = os.path.join(project_root, service)

    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    if service_root not in sys.path:
        sys.path.insert(0, service_root)


def _load_app(service: str, factory: Optional[str] = None) -> Any:
    """Dynamically load the FastAPI app from the service module."""
    _setup_path(service)
    module_name = f"{service}.main"
    module = importlib.import_module(module_name)

    if factory:
        obj = getattr(module, factory, None)
        if obj is None or not callable(obj):
            raise RuntimeError(f"Factory '{factory}' not found in {module_name}")
        return obj()
    else:
        app = getattr(module, "app", None)
        if app is None:
            raise RuntimeError(f"App 'app' not found in {module_name}")
        return app


def main():
    parser = argparse.ArgumentParser(description="Run CarbonIQ service")
    parser.add_argument(
        "--service",
        type=str,
        required=True,
        help="Service to run (ima_service, tenant_service, etc.)",
    )
    parser.add_argument(
        "--factory", type=str, default=None, help="Factory function to create the app"
    )
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Host to bind")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    parser.add_argument(
        "--workers",
        type=int,
        default=2,
        help="Number of workers (ignored with --reload)",
    )
    args = parser.parse_args()

    # Activate the venv for this service
    venv_path = SERVICE_VENVS.get(args.service)
    if not venv_path or not os.path.exists(venv_path):
        print(f"Error: No venv found for service '{args.service}' at {venv_path}")
        sys.exit(1)

    # Prepend venv site-packages to sys.path
    site_packages = os.path.join(
        venv_path,
        "lib",
        f"python{sys.version_info.major}.{sys.version_info.minor}",
        "site-packages",
    )
    if os.path.exists(site_packages):
        sys.path.insert(0, site_packages)

    log_level = "debug" if args.debug else "info"
    reload_flag = args.reload or args.debug

    if reload_flag and not args.factory:
        import_str = f"{args.service}.main:app"
        _setup_path(args.service)  # ensure reload subprocess imports correctly
        uvicorn.run(
            import_str,
            host=args.host,
            port=args.port,
            reload=True,
            log_level=log_level,
        )
    else:
        app = _load_app(args.service, args.factory)
        uvicorn.run(
            app,
            host=args.host,
            port=args.port,
            reload=reload_flag,
            log_level=log_level,
            workers=args.workers if not reload_flag else 1,
        )


if __name__ == "__main__":
    sys.exit(main())
