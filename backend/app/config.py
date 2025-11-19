# Configuration settings
import structlog

logger = structlog.get_logger()

class Config:
    LOG_LEVEL = "INFO"
    AGENT_TIMEOUT = 30
    MAX_STEPS = 10