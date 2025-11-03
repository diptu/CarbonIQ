"""Main entry point for Auth Service FastAPI application."""

from fastapi import FastAPI

from auth_service.app.api import auth_router

app = FastAPI(title="Auth Service", version="1.0.0")
app.include_router(auth_router)
