# app/services/audit_service.py
import json
import functools
import datetime
from typing import Callable, Optional, Any
from app.core.logger import logger
from app.core.config import get_settings

settings = get_settings()


def log_event(action: str, level: str = "INFO"):
    """
    Audit log decorator with structured logging.
    Automatically redacts sensitive fields like accessToken and refreshToken.
    """

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

            # Extract current_user if passed
            current_user = kwargs.get("current_user")
            if current_user:
                log_data["actor"] = getattr(current_user, "email", str(current_user))
                log_data["tenant"] = str(getattr(current_user, "tenant_id", None))
                log_data["created_by"] = str(getattr(current_user, "id", None))

            try:
                logger.debug(
                    f"Starting action: {action}, actor: {log_data['actor']}, tenant: {log_data['tenant']}"
                )
                result = await func(*args, **kwargs)

                # Determine target object safely and redact sensitive fields
                log_data["target"] = _extract_target(result)

                log_data["status"] = "success"
                if level.upper() == "INFO":
                    logger.info(
                        f"Action successful: {action}, actor: {log_data['actor']}, "
                        f"tenant: {log_data['tenant']}, target: {log_data['target']}"
                    )
                elif level.upper() == "ERROR":
                    logger.error(
                        f"Action successful (ERROR level): {action}, actor: {log_data['actor']}, "
                        f"tenant: {log_data['tenant']}, target: {log_data['target']}"
                    )
                return result

            except Exception as e:
                log_data["status"] = "error"
                log_data["detail"] = str(e)
                logger.error(
                    f"Action failed: {action}, actor: {log_data['actor']}, "
                    f"tenant: {log_data['tenant']}, error: {e}"
                )
                raise

            finally:
                # Write audit log to file
                try:
                    with open(settings.AUDIT_LOG_PATH, "a") as f:
                        f.write(json.dumps(log_data) + "\n")
                except Exception as log_exc:
                    logger.error(f"Failed to write audit log: {log_exc}")

        return wrapper

    return decorator


def _extract_target(result: Any) -> Optional[str]:
    """
    Safely extract a string identifier for logging.
    Redacts sensitive information like accessToken, refreshToken, and passwords.
    """
    if result is None:
        return None

    if hasattr(result, "model_dump"):  # Pydantic model
        result_dict = result.model_dump()
        return _extract_target(result_dict)

    if hasattr(result, "id"):
        return str(result.id)

    if isinstance(result, dict):
        safe_result = {}
        for k, v in result.items():
            if k.lower() in {"accesstoken", "refreshtoken", "password", "token"}:
                safe_result[k] = "***REDACTED***"
            elif isinstance(v, (dict, list)):
                safe_result[k] = _extract_target(v)
            else:
                safe_result[k] = v
        return str(safe_result)

    if isinstance(result, list):
        return str([_extract_target(item) for item in result])

    return str(result)
