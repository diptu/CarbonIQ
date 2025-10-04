# app/utils/audit.py
"""Audit logging utilities for role assignments and sensitive actions.

Pandas-style docstring
----------------------
This module provides file-based audit logging for tracking
important actions such as role assignments, permission changes,
or other security-related events. Each log entry is stored as a
JSON object on its own line (JSONL).

Notes
-----
- Audit logs are written to `AUDIT_LOG_PATH` defined in service
  configuration.
- Designed to be thread-safe via atomic file append.
- Can optionally include tenant_id to separate logs per tenant.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from ima_service.app.core.config import get_settings

settings = get_settings()

# Ensure log directory exists
log_path: Path = Path(settings.AUDIT_LOG_PATH)
log_path.parent.mkdir(parents=True, exist_ok=True)


def log_audit_event(
    actor_id: str,
    target_id: Optional[str],
    action: str,
    role: Optional[str] = None,
    tenant_id: Optional[str] = None,
    extra: Optional[dict[str, Any]] = None,
) -> None:
    """Log an audit event as a JSON object.

    Parameters
    ----------
    actor_id : str
        ID of the user performing the action.
    target_id : Optional[str]
        ID of the user or resource affected by the action.
    action : str
        Short description of the action (e.g., "assign_role").
    role : Optional[str]
        Role name if action involves a role assignment/removal.
    tenant_id : Optional[str]
        Tenant ID if action is tenant-scoped.
    extra : Optional[dict[str, Any]]
        Additional fields to store in the audit event.

    Notes
    -----
    - Each event is appended as a single JSON line to the audit log file.
    - Timestamp is added automatically in ISO 8601 UTC format.
    """
    event: dict[str, Any] = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "actor_id": actor_id,
        "target_id": target_id,
        "action": action,
        "role": role,
        "tenant_id": tenant_id,
    }

    if extra:
        event.update(extra)

    # Atomic append
    with log_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(event, ensure_ascii=False) + "\n")


def log_role_assignment(
    actor_id: str,
    target_user_id: str,
    role_name: str,
    tenant_id: Optional[str] = None,
) -> None:
    """Log a role assignment action for audit purposes.

    Parameters
    ----------
    actor_id : str
        ID of the user performing the role assignment.
    target_user_id : str
        ID of the user receiving the role.
    role_name : str
        Name of the assigned role.
    tenant_id : Optional[str], optional
        Tenant ID if scoped role, by default None.
    """
    log_audit_event(
        actor_id=actor_id,
        target_id=target_user_id,
        action="assign_role",
        role=role_name,
        tenant_id=tenant_id,
    )


def read_audit_log(limit: Optional[int] = None) -> list[dict[str, Any]]:
    """Read audit log entries from file.

    Parameters
    ----------
    limit : Optional[int]
        If provided, return only the last `limit` entries.

    Returns
    -------
    list[dict[str, Any]]
        List of audit events (chronological order: oldest first).
    """
    if not log_path.exists():
        return []

    with log_path.open("r", encoding="utf-8") as f:
        lines = f.readlines()

    events: list[dict[str, Any]] = [json.loads(line) for line in lines]

    if limit is not None:
        return events[-limit:]

    return events
