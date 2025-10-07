import logging
from app.core.config import get_settings

settings = get_settings()

logger = logging.getLogger("carboniq")
logger.setLevel(logging.DEBUG)  # Set default to DEBUG for dev

formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s - %(message)s")

# Console handler
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(formatter)
logger.addHandler(ch)

# Optional: File handler
fh = logging.FileHandler(settings.AUDIT_LOG_PATH)
fh.setLevel(logging.INFO)
fh.setFormatter(formatter)
logger.addHandler(fh)
