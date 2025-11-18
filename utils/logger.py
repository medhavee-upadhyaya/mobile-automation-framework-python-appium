import logging
from logging import Logger
from typing import Dict

_LOGGERS: Dict[str, Logger] = {}

DEFAULT_LOG_LEVEL = logging.INFO
LOG_FORMAT = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"


def _configure_root_logger() -> None:
    if not logging.getLogger().handlers:
        logging.basicConfig(level=DEFAULT_LOG_LEVEL, format=LOG_FORMAT)


def get_logger(name: str) -> Logger:
    """Return a module-level logger configured for the project."""
    if name in _LOGGERS:
        return _LOGGERS[name]

    _configure_root_logger()
    logger = logging.getLogger(name)
    logger.setLevel(DEFAULT_LOG_LEVEL)
    _LOGGERS[name] = logger
    return logger
