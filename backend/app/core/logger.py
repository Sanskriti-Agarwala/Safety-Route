"""
app/core/logger.py
Centralized logging configuration for Safety Route backend.
"""

import logging
import os
import sys
from typing import Optional

_loggers = {}
_configured = False


def _configure_logging() -> None:
    global _configured
    if _configured:
        return
    
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    env = os.getenv("ENV", "development").lower()
    
    if env == "development":
        log_level = "DEBUG"
    
    level = getattr(logging, log_level, logging.INFO)
    
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"
    
    logging.basicConfig(
        level=level,
        format=log_format,
        datefmt=date_format,
        stream=sys.stdout,
        force=True
    )
    
    _configured = True


def get_logger(name: str) -> logging.Logger:
    if name in _loggers:
        return _loggers[name]
    
    _configure_logging()
    
    logger = logging.getLogger(name)
    logger.propagate = True
    
    _loggers[name] = logger
    
    return logger


def set_log_level(level: str) -> None:
    _configure_logging()
    log_level = getattr(logging, level.upper(), logging.INFO)
    logging.getLogger().setLevel(log_level)