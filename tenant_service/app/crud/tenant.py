# tenant_service/app/crud/tenant.py
import logging
from typing import Dict, List
from uuid import uuid4

from sqlalchemy import select, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from shared_service.app.models.enums import PlanEnum, StatusEnum
from tenant_service.app.core.config import settings
from tenant_service.app.models.domain import TenantDomain
from tenant_service.app.models.membership import TenantMembership, TenantRole
from tenant_service.app.models.tenant import Tenant
from tenant_service.app.schemas.tenant import TenantCreate, TenantUpdate
from user_service.app.models.user import User

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)  # Enable debug logging

# BASE_DOMAIN = "carboniq.com"
BASE_DOMAIN = settings.BASE_DOMAIN


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

    def create(
        self, db: Session, tenant_in: TenantCreate, current_user: User = None
    ) -> Tenant:
        tenant_id = str(uuid4())
        status = tenant_in.status or StatusEnum.ACTIVE
        plan = tenant_in.plan or PlanEnum.FREE

        try:
            # 1. Insert tenant into public.tenants
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

            # 2. Create tenant-specific schema
            db.execute(text(f'CREATE SCHEMA IF NOT EXISTS "{schema_name}"'))
            db.commit()
            logger.debug(f"Schema '{schema_name}' created successfully")

            # 3. Insert primary domain (NOW schema exists)
            domain_name = f"{schema_name}.{BASE_DOMAIN}"

            domain = TenantDomain(
                tenant_id=tenant.id,
                domain=domain_name,
                is_primary=True,
                is_verified=False,
            )

            #  Force TenantDomain table back to public schema
            TenantDomain.__table__.schema = None
            db.add(domain)
            db.commit()
            db.refresh(domain)

            logger.info(
                f"Domain '{domain.domain}' auto-created for tenant '{tenant.name}' in schema '{schema_name}'"
            )
            SYSTEM_USER_ID = settings.SYSTEM_USER_ID
            # 4. Insert primary domainmembership (NOW schema exists)
            owner_user_id = getattr(current_user, "id", None) or SYSTEM_USER_ID
            owner_membership = TenantMembership(
                tenant_id=tenant.id,
                user_id=owner_user_id,
                tenant_role=TenantRole.OWNER,
                has_parent_access=True,
            )
            #  Force TenantDomain table back to public schema
            TenantMembership.__table__.schema = None
            db.add(owner_membership)
            db.commit()
            db.refresh(owner_membership)

            # 5. Create tenant-specific tables (with correct schema)
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

            # 6. Reset search_path
            db.execute(text("SET search_path TO public"))

            return tenant

        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Failed to create tenant '{tenant_in.name}': {e}")
            raise e

    # -------------------------------------
    # Tenant Update
    # -------------------------------------
    def update(self, db: Session, tenant: Tenant, tenant_in: TenantUpdate) -> Tenant:
        """
        Update tenant with cascade rules and detailed logging:
        - Only parent tenants can update plan/status, cascades to all descendants
        - Child/grandchild tenants inherit plan/status
        - Name can always be updated
        """
        update_fields: Dict = tenant_in.model_dump(exclude_unset=True)
        plan_changed = "plan" in update_fields
        status_changed = "status" in update_fields
        name_changed = "name" in update_fields

        logger.debug(
            f"Starting update for tenant {tenant.id} ('{tenant.name}') with fields: {update_fields}"
        )

        # Restrict child/grandchild from updating plan/status
        if tenant.parent_id and (plan_changed or status_changed):
            logger.warning(
                f"Tenant '{tenant.name}' is a child tenant; cannot update "
                f"{'plan and status' if plan_changed and status_changed else 'plan' if plan_changed else 'status'}"
            )
            raise ValueError(
                f"Tenant '{tenant.name}' is a child tenant and cannot modify "
                f"{'plan and status' if plan_changed and status_changed else 'plan' if plan_changed else 'status'} directly."
            )

        # Update name
        if name_changed:
            old_name = tenant.name
            tenant.name = update_fields["name"]
            logger.debug(f"Tenant name changed from '{old_name}' to '{tenant.name}'")

        # Update plan/status only for parent tenants
        if not tenant.parent_id:
            if plan_changed:
                old_plan = tenant.plan
                tenant.plan = update_fields["plan"]
                logger.info(
                    f"Tenant '{tenant.name}' plan changed from '{old_plan}' to '{tenant.plan}'"
                )
                self._cascade_plan(db, tenant.id, tenant.plan)

            if status_changed:
                old_status = tenant.status
                tenant.status = update_fields["status"]
                logger.info(
                    f"Tenant '{tenant.name}' status changed from '{old_status}' to '{tenant.status}'"
                )
                self._cascade_status(db, tenant.id, tenant.status)

        db.add(tenant)
        db.commit()
        db.refresh(tenant)

        logger.debug(
            f"Tenant '{tenant.name}' update complete. Current state: plan='{tenant.plan}', status='{tenant.status}'"
        )
        return tenant

    def _cascade_plan(self, db: Session, parent_id, new_plan):
        """Recursively update plan for all children with logging"""
        children = (
            db.execute(select(Tenant).where(Tenant.parent_id == parent_id))
            .scalars()
            .all()
        )
        logger.debug(
            f"Cascading plan '{new_plan}' for children of tenant {parent_id}: {len(children)} found"
        )
        for child in children:
            old_plan = child.plan
            child.plan = new_plan
            logger.info(
                f"Child tenant '{child.name}' plan updated from '{old_plan}' to '{new_plan}'"
            )
            db.add(child)
            self._cascade_plan(db, child.id, new_plan)
        db.commit()

    def _cascade_status(self, db: Session, parent_id, new_status):
        """Recursively update status for all children with logging"""
        children = (
            db.execute(select(Tenant).where(Tenant.parent_id == parent_id))
            .scalars()
            .all()
        )
        logger.debug(
            f"Cascading status '{new_status}' for children of tenant {parent_id}: {len(children)} found"
        )
        for child in children:
            old_status = child.status
            child.status = new_status
            logger.info(
                f"Child tenant '{child.name}' status updated from '{old_status}' to '{new_status}'"
            )
            db.add(child)
            self._cascade_status(db, child.id, new_status)
        db.commit()

    # ----------------------
    # Delete Tenant
    # ----------------------

    def delete(self, db, tenant_id, soft_delete=True, cascade_children=False):
        """
        Delete a tenant.
        :param db: SQLAlchemy session
        :param tenant_id: UUID of the tenant to delete
        :param soft_delete: If True, only mark as deleted. If False, hard delete including schema.
        :param cascade_children: If True, delete child tenants recursively.
        """
        tenant = db.get(Tenant, tenant_id)
        if not tenant:
            raise ValueError(f"Tenant with id {tenant_id} not found.")

        # Check if tenant has children
        if tenant.children and len(tenant.children) > 0:
            if cascade_children:
                # Recursively delete children
                for child in tenant.children:
                    self.delete(
                        db, child.id, soft_delete=soft_delete, cascade_children=True
                    )
            else:
                raise ValueError(
                    f"Tenant '{tenant.name}' has child tenants. Delete them first or set cascade_children=True."
                )

        if soft_delete:
            tenant.status = StatusEnum.DELETED
            db.add(tenant)
            db.commit()
        else:
            # Hard delete: drop schema
            try:
                if tenant.schema_name:
                    db.execute(
                        text(f'DROP SCHEMA IF EXISTS "{tenant.schema_name}" CASCADE')
                    )
                db.delete(tenant)
                db.commit()
            except SQLAlchemyError as e:
                db.rollback()
                raise RuntimeError(f"Failed to delete tenant '{tenant.name}': {e}")

    # -------------------------------------
    # Retrieval methods
    # -------------------------------------
    def get(self, db: Session, tenant_id: str) -> Tenant | None:
        return db.query(Tenant).filter(Tenant.id == tenant_id).first()

    def get_by_name(self, db: Session, name: str) -> Tenant | None:
        return db.query(Tenant).filter(Tenant.name == name).first()

    def get_by_schema(self, db: Session, schema_name: str) -> Tenant | None:
        return db.query(Tenant).filter(Tenant.schema_name == schema_name).first()

    def count(self, db: Session, active_only: bool = True) -> int:
        query = db.query(Tenant)
        if active_only:
            query = query.filter(Tenant.status == StatusEnum.ACTIVE)
        return query.count()

    def get_all(
        self, db: Session, skip: int = 0, limit: int = 10, active_only: bool = True
    ) -> List[Tenant]:
        query = db.query(Tenant)
        if active_only:
            query = query.filter(Tenant.status == StatusEnum.ACTIVE)
        return query.offset(skip).limit(limit).all()

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
