# app/services/audit_service.py
import json
import functools
import datetime
from typing import Callable
from app.core.logger import logger
from app.core.config import get_settings

settings = get_settings()


def log_event(action: str):
    """Audit log decorator with structured logging."""

    def decorator(func: Callable):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            log_data = {
                "timestamp": datetime.datetime.utcnow().isoformat(),
                "action": action,
                "actor": None,
                "target": None,
                "tenant": None,
                "status": None,
                "detail": None,
            }

            current_user = kwargs.get("current_user")
            if current_user:
                log_data["actor"] = getattr(current_user, "email", str(current_user))
                log_data["tenant"] = str(getattr(current_user, "tenant_id", None))

            try:
                logger.debug(
                    f"Starting action: {action}, actor: {log_data['actor']}, tenant: {log_data['tenant']}"
                )
                result = await func(*args, **kwargs)

                # Safe target detection
                if result is not None:
                    if hasattr(result, "id"):
                        log_data["target"] = str(result.id)
                    elif isinstance(result, dict) and "details" in result:
                        log_data["target"] = str(result.get("details"))

                log_data["status"] = "success"
                logger.info(
                    f"Action successful: {action}, actor: {log_data['actor']}, tenant: {log_data['tenant']}"
                )
                return result

            except Exception as e:
                log_data["status"] = "error"
                log_data["detail"] = str(e)
                logger.error(
                    f"Action failed: {action}, actor: {log_data['actor']}, tenant: {log_data['tenant']}, error: {e}"
                )
                raise e

            finally:
                # Write audit log to file
                with open(settings.AUDIT_LOG_PATH, "a") as f:
                    f.write(json.dumps(log_data) + "\n")

        return wrapper

    return decorator
