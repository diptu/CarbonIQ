# Config
# Middleware
# Shared response
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Routers
from gateway_service.app.api.v1.routes import auth, user
from gateway_service.app.core.config import settings
from gateway_service.app.middleware.audit import AuditMiddleware
from gateway_service.app.middleware.auth import AuthMiddleware
from gateway_service.app.middleware.tracing import TraceMiddleware

app = FastAPI(
    title="Gateway Service",
    version="1.0.0",
    description="API Gateway for User, Auth, and Tenant microservices",
)

# -----------------------------
# Middleware
# -----------------------------
app.add_middleware(TraceMiddleware)
app.add_middleware(AuthMiddleware)
app.add_middleware(AuditMiddleware)
# -----------------------------
# CORS
# -----------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------
# Routers
# -----------------------------
app.include_router(auth.router)
app.include_router(user.router)
# app.include_router(tenant.router)


# -----------------------------
# Root Endpoint
# -----------------------------
@app.get("/")
async def root():
    return {
        "service": settings.SERVICE_NAME,
        "version": settings.SERVICE_VERSION,
        "status": "running",
    }


# -----------------------------
# Optional Health Check
# -----------------------------
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": settings.SERVICE_NAME,
        "version": settings.SERVICE_VERSION,
    }
