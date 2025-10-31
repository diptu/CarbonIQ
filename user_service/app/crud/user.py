"""CRUD operations for User model."""

from typing import List, Optional
from uuid import UUID

from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserCRUD:
    """Provides CRUD operations for User entities."""

    def get(self, db: Session, user_id: UUID) -> Optional[User]:
        """Retrieve a user by their unique ID."""
        return db.query(User).filter(User.id == user_id).first()

    def get_by_email(self, db: Session, email: str) -> Optional[User]:
        """Retrieve a user by their email address."""
        return db.query(User).filter(User.email == email).first()

    def get_all(self, db: Session, skip: int = 0, limit: int = 100) -> List[User]:
        """Return a paginated list of users."""
        return db.query(User).offset(skip).limit(limit).all()

    def create(self, db: Session, obj_in: UserCreate) -> User:
        """Create a new user with a hashed password."""
        hashed_password = pwd_context.hash(obj_in.password)
        db_obj = User(
            email=obj_in.email,
            full_name=obj_in.full_name,
            hashed_password=hashed_password,
            is_active=obj_in.is_active,
            is_verified=obj_in.is_verified,
            is_superuser=obj_in.is_superuser,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(self, db: Session, db_obj: User, obj_in: UserUpdate) -> Optional[User]:
        """Update an existing user's details."""
        update_data = obj_in.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete(self, db: Session, user_id: UUID) -> Optional[User]:
        """Delete a user by ID."""
        db_obj = self.get(db, user_id)
        if db_obj:
            db.delete(db_obj)
            db.commit()
        return db_obj

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Check if a plaintext password matches a hashed password."""
        return bool(pwd_context.verify(plain_password, hashed_password))


user_crud = UserCRUD()
