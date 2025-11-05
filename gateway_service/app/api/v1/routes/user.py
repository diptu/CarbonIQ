from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse
from gateway_service.app.core.config import settings
from shared_service.app.core.deps import require_permissions

router = APIRouter(prefix="/users", tags=["users"])

USER_BASE = settings.USER_SERVICE_URL


@router.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy_user(
    path: str,
    request: Request,
    current_user=Depends(require_permissions(permissions=["user.read"])),
):
    """
    Generic proxy to User Service.
    """
    token = request.state.current_user.get("access_token")
    headers = dict(request.headers)
    headers["Authorization"] = f"Bearer {token}"
    body = await request.body()

    async with httpx.AsyncClient() as client:
        resp = await client.request(
            method=request.method,
            url=f"{USER_BASE}/{path}",
            headers=headers,
            content=body,
            params=request.query_params,
        )
    return JSONResponse(
        content=resp.json(),
        status_code=resp.status_code,
        headers={
            "X-Trace-ID": request.state.trace_id,
            "X-Correlation-ID": request.state.correlation_id,
        },
    )
