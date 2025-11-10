# tenant_service/app/core/utils.py

import re


def create_schema_name(slug: str) -> str:
    """
    Convert tenant slug into a valid PostgreSQL schema name.
    - Lowercase
    - Replace non-alphanumeric with underscores
    - Ensure it does not start with a digit
    """
    schema = re.sub(r"[^a-zA-Z0-9_]+", "_", slug.lower())

    if schema[0].isdigit():
        schema = f"t_{schema}"

    return schema


def run_tenant_migrations(schema_name: str):
    """
    Placeholder — alembic migrations disabled for now.
    We will add real logic later.
    """
    print(f"[SKIPPED] Migration for schema: {schema_name}")


def generate_unique_slug(db, name: str, model_class) -> str:
    """
    Generate a slug from the name and ensure it's unique in the database.
    - Converts name → lowercase, replaces spaces/special chars with "_"
    - Adds suffix if slug already exists
    """
    base_slug = re.sub(r"[^a-zA-Z0-9]+", "_", name.lower()).strip("_")
    slug = base_slug

    counter = 1
    while db.query(model_class).filter(model_class.slug == slug).first():
        slug = f"{base_slug}_{counter}"
        counter += 1

    return slug
