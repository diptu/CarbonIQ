# tenant_service/app/crud/tenant.py
import logging
import uuid

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from shared_service.app.models.enums import PlanEnum, StatusEnum
from tenant_service.app.models.domain import TenantDomain
from tenant_service.app.models.membership import TenantMembership
from tenant_service.app.models.tenant import Tenant
from tenant_service.app.schemas.tenant import TenantCreate

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)  # Set debug mode


class TenantCRUD:
    def create(self, db: Session, tenant_in: TenantCreate) -> Tenant:
        tenant_id = str(uuid.uuid4())
        status = tenant_in.status or StatusEnum.ACTIVE
        plan = tenant_in.plan or PlanEnum.FREE

        try:
            # -----------------------------
            # 1️⃣ Insert tenant into public.tenants
            # -----------------------------
            tenant = Tenant(
                id=tenant_id,
                name=tenant_in.name,
                status=status,
                plan=plan,
                parent_id=tenant_in.parent_id,
            )
            db.add(tenant)
            db.commit()
            db.refresh(tenant)
            logger.info(
                f"Tenant '{tenant_in.name}' created with schema '{tenant.schema_name}'"
            )

            schema_name = tenant.schema_name

            # -----------------------------
            # 2️⃣ Create tenant-specific schema
            # -----------------------------
            db.execute(text(f'CREATE SCHEMA IF NOT EXISTS "{schema_name}"'))
            db.commit()  # ✅ commit so schema is visible
            logger.debug(f"Schema '{schema_name}' created successfully")

            # -----------------------------
            # 3️⃣ Create tenant-specific tables dynamically
            # -----------------------------
            tables_to_create = [
                TenantMembership,
                TenantDomain,
            ]  # list all models to be created inside each schemas

            for model in tables_to_create:
                model.__table__.schema = schema_name
                model.__table__.create(bind=db.bind, checkfirst=True)
                logger.info(
                    f"Table '{model.__tablename__}' created in schema '{schema_name}'"
                )

            # -----------------------------
            # 4️⃣ Reset search_path to public (optional)
            # -----------------------------
            db.execute(text("SET search_path TO public"))

            return tenant

        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Failed to create tenant '{tenant_in.name}': {e}")
            raise e

    # -----------------------------
    # Retrieval methods
    # -----------------------------
    def get(self, db: Session, tenant_id: str) -> Tenant | None:
        return db.query(Tenant).filter(Tenant.id == tenant_id).first()

    def get_by_name(self, db: Session, name: str) -> Tenant | None:
        return db.query(Tenant).filter(Tenant.name == name).first()

    def get_by_schema(self, db: Session, schema_name: str) -> Tenant | None:
        return db.query(Tenant).filter(Tenant.schema_name == schema_name).first()


# Singleton instance
tenant_crud = TenantCRUD()
