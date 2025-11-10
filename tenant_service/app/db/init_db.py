# Import models package
import user_service.app.models  # noqa: F401
from user_service.app.db.session import engine
from user_service.app.models.base import Base

# Create all tables
Base.metadata.create_all(bind=engine)
