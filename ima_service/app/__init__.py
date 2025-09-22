# ima_service/app/__init__.py
"""IMA service application package (exposes __version__)."""

from importlib import metadata

try:
    __version__ = metadata.version("ima-service")
except metadata.PackageNotFoundError:
    __version__ = "0.0.0"
__all__ = ["__version__"]
