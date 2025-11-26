"""
CRUD operations for token blacklist management.
"""

from sqlalchemy.orm import Session

from auth_service.app.models.token_blacklist import TokenBlacklist


class TokenBlacklistCRUD:
    """CRUD operations for managing blacklisted tokens."""

    def add(self, db: Session, jti: str) -> TokenBlacklist:
        """
        Add a token to the blacklist.

        Args:
            db (Session): SQLAlchemy session.
            jti (str): JWT token identifier.

        Returns:
            TokenBlacklist: The created TokenBlacklist instance.
        """
        db_token = TokenBlacklist(jti=jti)
        db.add(db_token)
        db.commit()
        db.refresh(db_token)
        return db_token

    def is_blacklisted(self, db: Session, jti: str) -> bool:
        """
        Check if a token is blacklisted.

        Args:
            db (Session): SQLAlchemy session.
            jti (str): JWT token identifier.

        Returns:
            bool: True if the token is blacklisted, False otherwise.
        """
        return db.query(TokenBlacklist).filter(TokenBlacklist.jti == jti).first() is not None


token_blacklist_crud = TokenBlacklistCRUD()
