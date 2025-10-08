# app/services/audit_adapter.py
from __future__ import annotations
import json
import datetime
import functools
from typing import Callable, Optional, Any
import httpx
import sentry_sdk
from prometheus_client import Counter
from app.core.logger import logger
from app.core.config import get_settings

settings = get_settings()

# Prometheus metrics
AUDIT_SUCCESS = Counter(
    "audit_action_success_total", "Successful audit actions", ["action", "tenant"]
)
AUDIT_FAILURE = Counter(
    "audit_action_failure_total", "Failed audit actions", ["action", "tenant"]
)


class AuditAdapter:
    """
    Multi-destination audit logging: File, Loki, Sentry, Prometheus.
    """

    def __init__(self, loki_url: Optional[str] = None):
        self.loki_url = loki_url or settings.LOKI_URL

    async def _send_to_loki(self, log_data: dict) -> None:
        """Push structured log to Grafana Loki."""
        if not self.loki_url:
            return
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                await client.post(
                    url=f"{self.loki_url}/loki/api/v1/push",
                    json={
                        "streams": [
                            {
                                "labels": '{service="ima_service"}',
                                "entries": [
                                    {
                                        "ts": log_data["timestamp"],
                                        "line": json.dumps(log_data),
                                    }
                                ],
                            }
                        ]
                    },
                )
        except Exception as e:
            logger.error(f"Failed to send audit log to Loki: {e}")

    def _send_to_file(self, log_data: dict) -> None:
        """Append structured log to local file."""
        try:
            with open(settings.AUDIT_LOG_PATH, "a") as f:
                f.write(json.dumps(log_data) + "\n")
        except Exception as e:
            logger.error(f"Failed to write audit log to file: {e}")

    def _send_to_sentry(self, log_data: dict) -> None:
        """Send only errors to Sentry."""
        if log_data["status"] == "error":
            sentry_sdk.set_context(
                "user",
                {"email": log_data.get("actor"), "tenant": log_data.get("tenant")},
            )
            sentry_sdk.capture_message(
                f"Audit error: {log_data.get('action')} - {log_data.get('detail')}"
            )

    def _update_prometheus(self, log_data: dict) -> None:
        """Update Prometheus counters."""
        tenant = log_data.get("tenant", "unknown")
        if log_data["status"] == "success":
            AUDIT_SUCCESS.labels(action=log_data["action"], tenant=tenant).inc()
        else:
            AUDIT_FAILURE.labels(action=log_data["action"], tenant=tenant).inc()

    def log_event(
        self, action: str, extra: Optional[dict[str, Any]] = None
    ) -> Callable:
        """
        Decorator for async methods to audit events across multiple systems.

        Args:
            action: Action name.
            extra: Optional additional metadata.
        """

        def decorator(func: Callable):
            @functools.wraps(func)
            async def wrapper(*args, **kwargs):
                log_data: dict[str, Any] = {
                    "timestamp": datetime.datetime.utcnow().isoformat(),
                    "action": action,
                    "actor": None,
                    "target": None,
                    "tenant": None,
                    "status": None,
                    "detail": None,
                }
                if extra:
                    log_data.update(extra)

                current_user = kwargs.get("current_user")
                if current_user:
                    log_data["actor"] = getattr(
                        current_user, "email", str(current_user)
                    )
                    log_data["tenant"] = str(getattr(current_user, "tenant_id", None))

                try:
                    logger.debug(
                        f"Starting action: {action}, actor: {log_data['actor']}, "
                        f"tenant: {log_data['tenant']}"
                    )
                    result = await func(*args, **kwargs)

                    if result is not None:
                        if hasattr(result, "id"):
                            log_data["target"] = str(result.id)
                        elif isinstance(result, dict) and "id" in result:
                            log_data["target"] = str(result.get("id"))

                    log_data["status"] = "success"
                    logger.info(
                        f"Action successful: {action}, actor: {log_data['actor']}, "
                        f"tenant: {log_data['tenant']}"
                    )

                    # Prometheus metrics
                    self._update_prometheus(log_data)
                    # Send to file and Loki
                    self._send_to_file(log_data)
                    await self._send_to_loki(log_data)

                    return result

                except Exception as e:
                    log_data["status"] = "error"
                    log_data["detail"] = str(e)
                    logger.error(
                        f"Action failed: {action}, actor: {log_data['actor']}, "
                        f"tenant: {log_data['tenant']}, error: {e}"
                    )
                    # Prometheus metrics
                    self._update_prometheus(log_data)
                    # Send to file, Loki, Sentry
                    self._send_to_file(log_data)
                    await self._send_to_loki(log_data)
                    self._send_to_sentry(log_data)
                    raise e

            return wrapper

        return decorator


# Singleton instance for services to use
audit_adapter = AuditAdapter()
log_event = audit_adapter.log_event
