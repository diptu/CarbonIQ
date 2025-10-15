"""
Health check endpoint documentation.
"""

SERVER_HEALTH = {
    "summary": "Check server status",
    "description": """Verify that the IMA Service server is running.

**What you get**:
- `status`: `"ok"` if the server is reachable

**Example request**:

GET /v1/health/server

**Example response**:

```json
{
    "status": "ok"
}
```""",
}

DB_HEALTH = {
    "summary": "Database health check",
    "description": """Verify that the IMA Service database connection is working.

**What you get**:
- `status`: `"ok"` if the server is running
- `database`: `"connected"` if the database can be reached

**Errors**:
- 500 Internal Server Error if the database is unreachable.

**Example request**:

GET /v1/health/health

**Example response**:

```json
{
    "status": "ok",
    "database": "connected"
}
```""",
}
