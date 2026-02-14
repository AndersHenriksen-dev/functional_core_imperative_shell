"""Dataclass-based runtime configuration types."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class FileFormat(StrEnum):
    """Supported file formats."""

    CSV = "csv"
    PARQUET = "parquet"
    JSON = "json"
    EXCEL = "excel"
    FEATHER = "feather"
    ORC = "orc"
    PICKLE = "pickle"
    SQL = "sql"
    DELTA = "delta"


@dataclass(frozen=True)
class IOConfig:
    """IO configuration for a single dataframe."""

    path: str
    format: FileFormat
    options: dict[str, Any] = field(default_factory=dict)
    storage_options: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ScheduleConfig:
    """Schedule configuration for a domain."""

    enabled: bool = False
    cron: str = ""  # Cron expression (e.g., "0 2 * * *" for daily at 2am)
    interval: str = ""  # Interval type: "daily", "weekly", "monthly"
    day_of_week: str = "monday"  # For weekly: "monday", "tuesday", etc.
    day_of_month: int = 1  # For monthly: day of month (1-31)
    hour: int = 0  # Hour to run (0-23)
    minute: int = 0  # Minute to run (0-59)


@dataclass(frozen=True)
class DomainConfig:
    """Configuration for a domain pipeline."""

    name: str
    enabled: bool = True
    tags: list[str] = field(default_factory=list)
    inputs: dict[str, IOConfig] = field(default_factory=dict)
    outputs: dict[str, IOConfig] = field(default_factory=dict)
    params: dict[str, Any] = field(default_factory=dict)
    schedule: ScheduleConfig = field(default_factory=ScheduleConfig)


@dataclass(frozen=True)
class LoggingConfig:
    """Logging configuration."""

    level: str = "INFO"
    log_dir: str = "logs"
    to_console: bool = True
    to_file: bool = True


@dataclass(frozen=True)
class ThreadExecutionConfig:
    """Threaded execution configuration."""

    enabled: bool = False
    max_workers: int | None = None


@dataclass(frozen=True)
class ProcessExecutionConfig:
    """Process execution configuration."""

    enabled: bool = False
    max_workers: int | None = None


@dataclass(frozen=True)
class ParallelExecutionConfig:
    """Parallel execution configuration."""

    threads: ThreadExecutionConfig = field(default_factory=ThreadExecutionConfig)
    processes: ProcessExecutionConfig = field(default_factory=ProcessExecutionConfig)


@dataclass(frozen=True)
class ExecutionConfig:
    """Execution configuration."""

    parallel: ParallelExecutionConfig = field(default_factory=ParallelExecutionConfig)


@dataclass(frozen=True)
class GlobalConfig:
    """Top-level application configuration."""

    env: str
    logging: LoggingConfig
    execution: ExecutionConfig = field(default_factory=ExecutionConfig)
    inputs: dict[str, IOConfig] = field(default_factory=dict)
    active_domains: list[str] = field(default_factory=list)
    active_tags: list[str] = field(default_factory=list)
    domains: dict[str, DomainConfig] = field(default_factory=dict)
