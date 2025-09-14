"""
File: app/api/v1/health/__init__.py
Package entrypoint for health API.

This package provides all endpoints and utilities related to API and
service health checks. It exposes the router to be included in the main
FastAPI application.
"""

from .router import router

__all__ = ["router"]
