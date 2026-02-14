"""Logging setup with optional domain context."""

from __future__ import annotations

import logging
import logging.config
import os
import sys
from dataclasses import asdict
from datetime import datetime
from typing import Any

from insert_package_name.schema.types import LoggingConfig


class _DomainFilter(logging.Filter):
    """Ensure a domain attribute exists for formatters."""

    def filter(self, record: logging.LogRecord) -> bool:
        """Attach a default domain attribute when missing.

        Parameters
        ----------
        record : logging.LogRecord
            Log record to enrich.

        Returns
        -------
        bool
            True to keep the record.

        """
        if not hasattr(record, "domain"):
            record.domain = "-"
        return True


def configure_logging(cfg: LoggingConfig) -> None:
    """Configure logging for console and optional file output.

    Parameters
    ----------
    cfg : LoggingConfig
        Logging configuration.

    """
    os.makedirs(cfg.log_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d_%H.%M.%S")
    log_file = os.path.join(cfg.log_dir, f"run_{timestamp}.log")

    handlers: dict[str, dict[str, Any]] = {}
    handler_names: list[str] = []

    if cfg.to_console:
        handlers["console"] = {
            "class": "logging.StreamHandler",
            "formatter": "simple",
            "filters": ["domain"],
            "level": cfg.level,
        }
        handler_names.append("console")

    if cfg.to_file:
        handlers["file"] = {
            "class": "logging.FileHandler",
            "formatter": "detailed",
            "filters": ["domain"],
            "filename": log_file,
            "level": cfg.level,
        }
        handler_names.append("file")

    logging_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "filters": {"domain": {"()": _DomainFilter}},
        "formatters": {
            "simple": {
                "format": "%(levelname)s [%(domain)s] %(message)s",
            },
            "detailed": {
                "format": "%(asctime)s %(levelname)s [%(domain)s] %(name)s:%(lineno)d - %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
        },
        "handlers": handlers,
        "root": {
            "handlers": handler_names,
            "level": cfg.level,
            "filters": ["domain"],
        },
    }

    logging.config.dictConfig(logging_config)

    if cfg.to_file:
        logging.getLogger(__name__).info("Logging to %s", log_file)

    def _log_unhandled_exceptions(exc_type, exc_value, exc_traceback):
        """Log unhandled exceptions through the root logger."""
        logging.critical("Unhandled exception", exc_info=(exc_type, exc_value, exc_traceback))

    sys.excepthook = _log_unhandled_exceptions


def get_logger(name: str) -> logging.Logger:
    """Get a logger by name.

    Parameters
    ----------
    name : str
        Logger name.

    Returns
    -------
    logging.Logger
        Logger instance.

    """
    return logging.getLogger(name)


def get_domain_logger(name: str, domain: str) -> logging.LoggerAdapter:
    """Get a logger that includes a domain context.

    Parameters
    ----------
    name : str
        Logger name.
    domain : str
        Domain identifier to add to log records.

    Returns
    -------
    logging.LoggerAdapter
        Logger adapter with domain context.

    """
    logger = logging.getLogger(name)
    return logging.LoggerAdapter(logger, extra={"domain": domain})


def logging_config_to_dict(cfg: LoggingConfig) -> dict[str, Any]:
    """Serialize logging config for diagnostics.

    Parameters
    ----------
    cfg : LoggingConfig
        Logging configuration.

    Returns
    -------
    dict[str, Any]
        Dictionary representation of the config.

    """
    return asdict(cfg)
