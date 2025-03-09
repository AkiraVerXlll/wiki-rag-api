import logging
import sys
from pathlib import Path
from typing import Optional

from loguru import logger

LOGS_DIR = Path("logs")
LOGS_DIR.mkdir(exist_ok=True)

def setup_logging(log_level: str = "INFO", log_file: Optional[str] = None) -> None:
    """
    Configure logging for the application using loguru.

    :param log_level: The logging level to use (default: "INFO")
    :param log_file: Optional path to log file (default: None)
    """
    logger.remove()

    logger.add(
        sys.stderr,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level=log_level,
        colorize=True
    )

    if log_file:
        log_path = LOGS_DIR / log_file
        logger.add(
            log_path,
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
            level=log_level,
            rotation="500 MB",
            retention="10 days",
            compression="zip"
        )

class InterceptHandler(logging.Handler):
    """
    Intercept standard library logging and redirect to loguru.
    """
    def emit(self, record):
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )

def setup_fastapi_logging() -> None:
    """
    Configure FastAPI to use loguru for logging.
    """
    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)

    logging.getLogger("uvicorn.access").handlers = [InterceptHandler()]

    for name in logging.root.manager.loggerDict:
        if name.startswith("uvicorn"):
            logging.getLogger(name).handlers = [InterceptHandler()] 