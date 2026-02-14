"""Tests for logging configuration."""

from __future__ import annotations

from pathlib import Path

from insert_package_name.core.logging import configure_logging, get_domain_logger
from insert_package_name.schema.types import LoggingConfig


def test_configure_logging_writes_file(tmp_path: Path) -> None:
    cfg = LoggingConfig(level="INFO", log_dir=str(tmp_path), to_console=False, to_file=True)
    configure_logging(cfg)

    log_files = list(tmp_path.glob("*.log"))
    assert log_files, "Expected a log file to be created"


def test_get_domain_logger_includes_domain() -> None:
    logger = get_domain_logger("test", "domain-a")
    assert logger.extra["domain"] == "domain-a"
