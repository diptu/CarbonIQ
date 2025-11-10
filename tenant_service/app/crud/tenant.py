# tenant_service/app/crud/tenant.py
import logging
import uuid

from sqlalchemy import text
from sqlalchemy.orm import Session

from shared_service.app.models.enums import PlanEnum, StatusEnum
from tenant_service.app.core.utils import generate_unique_slug
from tenant_service.app.models.tenant import Tenant
from tenant_service.app.schemas.tenant import TenantCreate

logger = logging.getLogger(__name__)


class TenantCRUD:
    def create(self, db: Session, tenant_in: TenantCreate) -> Tenant:
        tenant_id = str(uuid.uuid4())
        # Generate a unique slug for schema and tenant
        slug = generate_unique_slug(name=tenant_in.name, model_class=Tenant, db=db)
        schema_name = slug.lower()

        # Use default enums if not provided
        status = (tenant_in.status or StatusEnum.ACTIVE).value
        plan = (tenant_in.plan or PlanEnum.FREE).value

        try:
            # Insert tenant in public.tenants
            db.execute(
                text(
                    """
                    INSERT INTO public.tenants (id, name, slug, status, plan)
                    VALUES (:id, :name, :slug, :status, :plan)
                    RETURNING id, name, slug, status, plan
                    """
                ),
                {
                    "id": tenant_id,
                    "name": tenant_in.name,
                    "slug": schema_name,
                    "status": status,
                    "plan": plan,
                },
            )
            db.commit()
            logger.info(f"Tenant '{tenant_in.name}' inserted into public.tenants")

            # Create tenant-specific schema
            db.execute(text(f'CREATE SCHEMA IF NOT EXISTS "{schema_name}"'))
            logger.debug(f"Schema '{schema_name}' created successfully")

            # Create tenant-specific tables
            db.execute(
                text(f"""
                CREATE TABLE IF NOT EXISTS "{schema_name}"."tenant_memberships" (
                    id UUID PRIMARY KEY,
                    tenant_id UUID NOT NULL REFERENCES public.tenants(id),
                    user_id UUID NOT NULL,
                    tenant_role VARCHAR NOT NULL DEFAULT 'MEMBER',
                    is_active BOOLEAN NOT NULL DEFAULT TRUE
                );
                """)
            )
            db.execute(
                text(f"""
                CREATE TABLE IF NOT EXISTS "{schema_name}"."tenant_domains" (
                    id UUID PRIMARY KEY,
                    tenant_id UUID NOT NULL REFERENCES public.tenants(id),
                    domain VARCHAR NOT NULL UNIQUE,
                    is_verified BOOLEAN DEFAULT FALSE
                );
                """)
            )
            db.commit()
            logger.info(f"Tenant-specific tables created in schema '{schema_name}'")

            return Tenant(
                id=tenant_id,
                name=tenant_in.name,
                slug=schema_name,
                status=StatusEnum(status),
                plan=PlanEnum(plan),
            )

        except Exception as e:
            db.rollback()
            logger.error(f"Failed to create tenant '{tenant_in.name}': {e}")
            raise e

    # -----------------------------
    # Retrieval methods
    # -----------------------------
    def get(self, db: Session, tenant_id: str) -> Tenant | None:
        """Get tenant by ID"""
        result = db.execute(
            text(
                "SELECT id, name, slug, status, plan FROM public.tenants WHERE id = :id"
            ),
            {"id": tenant_id},
        ).first()
        if result:
            return Tenant(
                id=result.id,
                name=result.name,
                slug=result.slug,
                status=StatusEnum(result.status),
                plan=PlanEnum(result.plan),
            )
        return None

    def get_by_name(self, db: Session, name: str) -> Tenant | None:
        """Get tenant by name"""
        result = db.execute(
            text(
                "SELECT id, name, slug, status, plan FROM public.tenants WHERE name = :name"
            ),
            {"name": name},
        ).first()
        if result:
            return Tenant(
                id=result.id,
                name=result.name,
                slug=result.slug,
                status=StatusEnum(result.status),
                plan=PlanEnum(result.plan),
            )
        return None

    def get_by_slug(self, db: Session, slug: str) -> Tenant | None:
        """Get tenant by slug"""
        result = db.execute(
            text(
                "SELECT id, name, slug, status, plan FROM public.tenants WHERE slug = :slug"
            ),
            {"slug": slug},
        ).first()
        if result:
            return Tenant(
                id=result.id,
                name=result.name,
                slug=result.slug,
                status=StatusEnum(result.status),
                plan=PlanEnum(result.plan),
            )
        return None


# Singleton instance
tenant_crud = TenantCRUD()
