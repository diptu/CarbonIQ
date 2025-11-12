# tenant_service/app/crud/tenant.py
import logging
import uuid
from typing import List

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from shared_service.app.models.enums import PlanEnum, StatusEnum
from tenant_service.app.models.domain import TenantDomain
from tenant_service.app.models.membership import TenantMembership
from tenant_service.app.models.tenant import Tenant
from tenant_service.app.schemas.tenant import TenantCreate

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)  # Enable debug logging


class TenantCRUD:
    # -------------------------------------
    # INTERNAL SHARED UPDATE METHOD
    # -------------------------------------
    def _update_status(
        self, db: Session, tenant_id: str, new_status: StatusEnum, action: str
    ) -> Tenant:
        """
        Update tenant status with hierarchical rules:
        - Child cannot be active if parent is inactive
        - Parent status changes cascade to children (deactivate/suspend)
        """
        try:
            tenant = self.get(db, tenant_id)
            if not tenant:
                logger.error(f"{action}(): Tenant '{tenant_id}' not found")
                raise ValueError(f"Tenant with id '{tenant_id}' not found")

            # ❌ Block child activation if parent is inactive
            if new_status == StatusEnum.ACTIVE and tenant.parent_id:
                parent = self.get(db, tenant.parent_id)
                if parent and parent.status != StatusEnum.ACTIVE:
                    raise ValueError(
                        f"Cannot activate tenant '{tenant.name}' because parent "
                        f"'{parent.name}' is {parent.status.value}"
                    )

            if tenant.status == new_status:
                logger.info(f"Tenant '{tenant.name}' is already {new_status.value}")
                return tenant

            # ✅ Update tenant status
            tenant.status = new_status
            db.commit()
            db.refresh(tenant)
            logger.info(f"Tenant '{tenant.name}' {action} successfully")

            # ✅ Cascade only if this tenant is a parent
            if not tenant.parent_id and new_status in (
                StatusEnum.INACTIVE,
                StatusEnum.SUSPENDED,
            ):
                db.execute(
                    text("""
                        UPDATE tenants
                        SET status = :status
                        WHERE parent_id = :parent_id
                    """),
                    {"status": new_status.value, "parent_id": tenant.id},
                )
                db.commit()
                logger.info(
                    f"Cascaded {action} to all child tenants of '{tenant.name}'"
                )

            return tenant

        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Failed to {action} tenant '{tenant_id}': {e}")
            raise e

    # -------------------------------------
    # Tenant Creation
    # -------------------------------------
    def create(self, db: Session, tenant_in: TenantCreate) -> Tenant:
        tenant_id = str(uuid.uuid4())
        status = tenant_in.status or StatusEnum.ACTIVE
        plan = tenant_in.plan or PlanEnum.FREE

        try:
            # 1️⃣ Insert tenant into public.tenants
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

            # 2️⃣ Create tenant-specific schema
            db.execute(text(f'CREATE SCHEMA IF NOT EXISTS "{schema_name}"'))
            db.commit()
            logger.debug(f"Schema '{schema_name}' created successfully")

            # 3️⃣ Create tenant-specific tables dynamically
            tables_to_create = [
                TenantMembership,
                TenantDomain,
            ]
            for model in tables_to_create:
                model.__table__.schema = schema_name
                model.__table__.create(bind=db.bind, checkfirst=True)
                logger.info(
                    f"Table '{model.__tablename__}' created in schema '{schema_name}'"
                )

            # 4️⃣ Reset search_path to public
            db.execute(text("SET search_path TO public"))

            return tenant

        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Failed to create tenant '{tenant_in.name}': {e}")
            raise e

    # -------------------------------------
    # Retrieval methods
    # -------------------------------------
    def get(self, db: Session, tenant_id: str) -> Tenant | None:
        return db.query(Tenant).filter(Tenant.id == tenant_id).first()

    def get_by_name(self, db: Session, name: str) -> Tenant | None:
        return db.query(Tenant).filter(Tenant.name == name).first()

    def get_by_schema(self, db: Session, schema_name: str) -> Tenant | None:
        return db.query(Tenant).filter(Tenant.schema_name == schema_name).first()

    def count(self, db: Session) -> int:
        return db.query(Tenant).count()

    def get_all(self, db: Session, skip: int = 0, limit: int = 10) -> List[Tenant]:
        return db.query(Tenant).offset(skip).limit(limit).all()

    # -------------------------------------
    # Status Change Methods
    # -------------------------------------
    def activate(self, db: Session, tenant_id: str) -> Tenant:
        return self._update_status(db, tenant_id, StatusEnum.ACTIVE, "activated")

    def suspend(self, db: Session, tenant_id: str) -> Tenant:
        return self._update_status(db, tenant_id, StatusEnum.SUSPENDED, "suspended")

    def deactivate(self, db: Session, tenant_id: str) -> Tenant:
        return self._update_status(db, tenant_id, StatusEnum.INACTIVE, "deactivated")


# Singleton instance
tenant_crud = TenantCRUD()
