"""
Async CRUD operations for token blacklist management.
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from auth_service.app.models.token_blacklist import TokenBlacklist


class TokenBlacklistCRUD:
    """Async CRUD operations for managing blacklisted tokens."""

    async def add(self, db: AsyncSession, jti: str) -> TokenBlacklist:
        """
        Add a token to the blacklist asynchronously.

        Args:
            db (AsyncSession): SQLAlchemy async session.
            jti (str): JWT token identifier.

        Returns:
            TokenBlacklist: The created TokenBlacklist instance.
        """
        db_token = TokenBlacklist(jti=jti)
        db.add(db_token)
        await db.commit()
        await db.refresh(db_token)
        return db_token

    async def is_blacklisted(self, db: AsyncSession, jti: str) -> bool:
        """
        Check asynchronously if a token is blacklisted.

        Args:
            db (AsyncSession): SQLAlchemy async session.
            jti (str): JWT token identifier.

        Returns:
            bool: True if the token is blacklisted, False otherwise.
        """
        query = select(TokenBlacklist).where(TokenBlacklist.jti == jti)
        result = await db.execute(query)
        return result.scalar_one_or_none() is not None


token_blacklist_crud = TokenBlacklistCRUD()
