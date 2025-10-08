# app/core/logger.py
import logging
from app.core.config import get_settings

settings = get_settings()

logger = logging.getLogger("carboniq:ima")

# Use DEBUG level when DEBUG=True, else INFO
log_level = logging.DEBUG if settings.DEBUG else logging.INFO
logger.setLevel(log_level)

formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s - %(message)s")

# Console handler
ch = logging.StreamHandler()
ch.setLevel(log_level)
ch.setFormatter(formatter)
logger.addHandler(ch)

# Optional: File handler (only if AUDIT_LOG_PATH is defined)
if getattr(settings, "AUDIT_LOG_PATH", None):
    fh = logging.FileHandler(settings.AUDIT_LOG_PATH)
    fh.setLevel(logging.INFO)
    fh.setFormatter(formatter)
    logger.addHandler(fh)
