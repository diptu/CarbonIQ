from sqlalchemy import text

from tenant_service.app.db.session import engine

with engine.connect() as conn:
    conn = conn.execution_options(isolation_level="AUTOCOMMIT")
    conn.execute(text("CREATE SCHEMA IF NOT EXISTS test_schema_debug"))
    res = conn.execute(text("SELECT schema_name FROM information_schema.schemata"))
    print([r[0] for r in res])
