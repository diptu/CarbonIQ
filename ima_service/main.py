"""Entry point for the IMA FastAPI service.

This module boots the FastAPI app with uvicorn. Configuration is read from
environment variables so you can tweak behavior without code changes.

Environment Variables
---------------------
HOST : str, default "127.0.0.1"
    Bind address for the server.
PORT : int, default 8000
    TCP port to listen on.
RELOAD : bool, default "false"
    Enable auto-reload (dev only). Ignored in multi-worker mode.
LOG_LEVEL : str, default "info"
    Uvicorn log level: "critical", "error", "warning", "info", "debug".
WORKERS : int, default 1
    Number of worker processes. Must be 1 if RELOAD=true.
PROXY_HEADERS : bool, default "true"
    Enable proxy header parsing (X-Forwarded-For, etc.).
FORWARDED_ALLOW_IPS : str, default "*"
    Comma-separated list of proxy IPs allowed to set forwarding headers.

Examples
--------
Run with defaults
>>> python -m ima_service.main  # doctest: +SKIP

Custom port and reload (dev)
>>> PORT=9000 RELOAD=true python -m ima_service.main  # doctest: +SKIP
"""

from __future__ import annotations

import os
from typing import Literal

import uvicorn

from ima_service.app.main import create_app


def _get_env(name: str, default: str) -> str:
    """Return environment variable `name` or `default` if unset.

    Parameters
    ----------
    name : str
        Environment variable name.
    default : str
        Default value if the variable is not set.

    Returns
    -------
    str
        The environment value or default.
    """
    return os.getenv(name, default)


def _get_int(name: str, default: int) -> int:
    """Parse an int from an environment variable.

    Parameters
    ----------
    name : str
        Environment variable name.
    default : int
        Default value if parsing fails or variable is unset.

    Returns
    -------
    int
        Parsed integer or default.
    """
    raw = os.getenv(name)
    if raw is None:
        return default
    try:
        return int(raw)
    except ValueError:
        return default


def _get_bool(name: str, default: bool) -> bool:
    """Parse a boolean from an environment variable.

    Truthy: "1", "true", "yes", "y", "on" (case-insensitive)
    Falsy : "0", "false", "no", "n", "off" (case-insensitive)

    Parameters
    ----------
    name : str
        Environment variable name.
    default : bool
        Default value if variable is unset or unparsable.

    Returns
    -------
    bool
        Parsed boolean or default.
    """
    raw = os.getenv(name)
    if raw is None:
        return default
    val = raw.strip().lower()
    if val in {"1", "true", "yes", "y", "on"}:
        return True
    if val in {"0", "false", "no", "n", "off"}:
        return False
    return default


def run() -> None:
    """Start the uvicorn server with environment-driven settings.

    Notes
    -----
    - When ``RELOAD=true``, uvicorn uses a single worker. If ``WORKERS`` is
      greater than 1, it will be ignored to keep reload stable.
    - ``PROXY_HEADERS`` and ``FORWARDED_ALLOW_IPS`` help when running
      behind reverse proxies (e.g., Nginx, Traefik, Kubernetes Ingress).
    """
    host = _get_env("HOST", "127.0.0.1")
    port = _get_int("PORT", 8000)
    reload_ = _get_bool("RELOAD", False)
    log_level: Literal[
        "critical", "error", "warning", "info", "debug"
    ] = _get_env(
        "LOG_LEVEL", "info"
    )  # type: ignore[assignment]
    workers = _get_int("WORKERS", 1)
    proxy_headers = _get_bool("PROXY_HEADERS", True)
    forwarded_allow_ips = _get_env("FORWARDED_ALLOW_IPS", "*")

    # Respect reload semantics: single-process only.
    if reload_:
        workers = 1

    app = create_app()

    config = uvicorn.Config(
        app=app,
        host=host,
        port=port,
        reload=reload_,
        log_level=log_level,
        workers=workers,
        proxy_headers=proxy_headers,
        forwarded_allow_ips=forwarded_allow_ips,
    )
    server = uvicorn.Server(config)
    server.run()


if __name__ == "__main__":
    run()
