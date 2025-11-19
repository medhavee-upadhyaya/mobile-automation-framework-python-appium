import logging
import os
from logging import Logger
from pathlib import Path
from typing import Dict

_LOGGERS: Dict[str, Logger] = {}

DEFAULT_LOG_LEVEL = os.getenv("FRAMEWORK_LOG_LEVEL", "INFO").upper()
LOG_FORMAT = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
LOG_DIR = Path(__file__).resolve().parents[1] / "reports" / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOG_DIR / "framework.log"


def _configure_root_logger() -> None:
    root_logger = logging.getLogger()
    if root_logger.handlers:
        return

    root_logger.setLevel(DEFAULT_LOG_LEVEL)

    formatter = logging.Formatter(LOG_FORMAT)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)


def get_logger(name: str) -> Logger:
    """Return a module-level logger configured for the project."""
    if name in _LOGGERS:
        return _LOGGERS[name]

    _configure_root_logger()
    logger = logging.getLogger(name)
    _LOGGERS[name] = logger
    return logger
