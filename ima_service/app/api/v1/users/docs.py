# app/api/v1/users/docs.py
"""Reusable OpenAPI examples for Users."""

from __future__ import annotations

create_example = {
    "summary": "Register a user",
    "value": {
        "email": "alice@example.com",
        "password": "Str0ngP@ss!",
        "username": "alice",
        "role": "USER",
    },
}

update_example = {
    "summary": "Promote to moderator",
    "value": {"role": "MODERATOR"},
}
