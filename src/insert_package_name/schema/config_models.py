"""Pydantic models for configuration validation."""

from __future__ import annotations

from typing import Any

from apscheduler.triggers.cron import CronTrigger
from pydantic import BaseModel, ConfigDict, Field, model_validator

from insert_package_name.schema.types import (
    DomainConfig,
    ExecutionConfig,
    FileFormat,
    GlobalConfig,
    IOConfig,
    LoggingConfig,
    ParallelExecutionConfig,
    ProcessExecutionConfig,
    ScheduleConfig,
    TagType,
    ThreadExecutionConfig,
)


class IOConfigModel(BaseModel):
    """Pydantic model for IO config validation."""

    model_config = ConfigDict(extra="forbid")

    path: str
    format: FileFormat
    options: dict[str, Any] = Field(default_factory=dict)
    storage_options: dict[str, Any] = Field(default_factory=dict)

    def to_dataclass(self) -> IOConfig:
        """Convert the validated model to a dataclass.

        Returns
        -------
        IOConfig
            Dataclass representation.

        """
        return IOConfig(
            path=self.path,
            format=self.format,
            options=dict(self.options),
            storage_options=dict(self.storage_options),
        )


class ScheduleConfigModel(BaseModel):
    """Pydantic model for schedule validation."""

    model_config = ConfigDict(extra="forbid")

    enabled: bool = False
    cron: str = ""
    interval: str = ""  # "daily", "weekly", "monthly"
    day_of_week: str = "monday"
    day_of_month: int = 1
    hour: int = 0
    minute: int = 0

    @model_validator(mode="after")
    def validate_schedule(self) -> ScheduleConfigModel:
        """Validate schedule settings and cron syntax."""
        if not self.enabled:
            return self

        has_cron = bool(self.cron)
        has_interval = bool(self.interval)

        if has_cron and has_interval:
            raise ValueError("Provide either 'cron' or 'interval', not both.")
        if not has_cron and not has_interval:
            raise ValueError("Schedule enabled requires 'cron' or 'interval'.")

        if has_cron:
            try:
                CronTrigger.from_crontab(self.cron)
            except ValueError as exc:
                raise ValueError(f"Invalid cron expression: {self.cron}") from exc
            return self

        allowed_intervals = {"daily", "weekly", "monthly"}
        if self.interval not in allowed_intervals:
            allowed_list = ", ".join(sorted(allowed_intervals))
            raise ValueError(f"Invalid interval '{self.interval}'. Use one of: {allowed_list}.")

        if not 0 <= self.hour <= 23:
            raise ValueError("hour must be between 0 and 23.")
        if not 0 <= self.minute <= 59:
            raise ValueError("minute must be between 0 and 59.")

        if self.interval == "weekly":
            valid_days = {
                "monday",
                "tuesday",
                "wednesday",
                "thursday",
                "friday",
                "saturday",
                "sunday",
            }
            day = self.day_of_week.lower()
            if day not in valid_days:
                valid_list = ", ".join(sorted(valid_days))
                raise ValueError(f"Invalid day_of_week '{self.day_of_week}'. Use one of: {valid_list}.")
            self.day_of_week = day

        if self.interval == "monthly" and not 1 <= self.day_of_month <= 31:
            raise ValueError("day_of_month must be between 1 and 31.")

        return self

    def to_dataclass(self) -> ScheduleConfig:
        """Convert the validated model to a dataclass.

        Returns
        -------
        ScheduleConfig
            Dataclass representation.

        """
        return ScheduleConfig(
            enabled=self.enabled,
            cron=self.cron,
            interval=self.interval,
            day_of_week=self.day_of_week,
            day_of_month=self.day_of_month,
            hour=self.hour,
            minute=self.minute,
        )


class DomainConfigModel(BaseModel):
    """Pydantic model for domain validation."""

    model_config = ConfigDict(extra="forbid")

    name: str
    enabled: bool = True
    tags: list[str] = Field(default_factory=list)
    inputs: dict[str, IOConfigModel] | list[str] = Field(default_factory=dict)
    outputs: dict[str, IOConfigModel] = Field(default_factory=dict)
    params: dict[str, Any] = Field(default_factory=dict)
    schedule: ScheduleConfigModel = Field(default_factory=ScheduleConfigModel)

    def to_dataclass(self) -> DomainConfig:
        """Convert the validated model to a dataclass.

        Returns
        -------
        DomainConfig
            Dataclass representation.

        """
        if isinstance(self.inputs, list):
            raise ValueError("Domain inputs must be resolved to a mapping before conversion.")
        return DomainConfig(
            name=self.name,
            enabled=self.enabled,
            tags=list(self.tags),
            inputs={key: value.to_dataclass() for key, value in self.inputs.items()},
            outputs={key: value.to_dataclass() for key, value in self.outputs.items()},
            params=dict(self.params),
            schedule=self.schedule.to_dataclass(),
        )


class LoggingConfigModel(BaseModel):
    """Pydantic model for logging validation."""

    model_config = ConfigDict(extra="forbid")

    level: str = "INFO"
    log_dir: str = "logs"
    to_console: bool = True
    to_file: bool = True

    def to_dataclass(self) -> LoggingConfig:
        """Convert the validated model to a dataclass.

        Returns
        -------
        LoggingConfig
            Dataclass representation.

        """
        return LoggingConfig(
            level=self.level,
            log_dir=self.log_dir,
            to_console=self.to_console,
            to_file=self.to_file,
        )


class ThreadExecutionConfigModel(BaseModel):
    """Pydantic model for thread execution settings."""

    model_config = ConfigDict(extra="forbid")

    enabled: bool = False
    max_workers: int | None = None

    @model_validator(mode="after")
    def validate_threads(self) -> ThreadExecutionConfigModel:
        """Validate thread execution settings."""
        if self.max_workers is not None and self.max_workers < 1:
            raise ValueError("threads.max_workers must be >= 1 when provided.")
        return self

    def to_dataclass(self) -> ThreadExecutionConfig:
        """Convert the validated model to a dataclass.

        Returns
        -------
        ThreadExecutionConfig
            Dataclass representation.

        """
        return ThreadExecutionConfig(
            enabled=self.enabled,
            max_workers=self.max_workers,
        )


class ProcessExecutionConfigModel(BaseModel):
    """Pydantic model for process execution settings."""

    model_config = ConfigDict(extra="forbid")

    enabled: bool = False
    max_workers: int | None = None

    @model_validator(mode="after")
    def validate_processes(self) -> ProcessExecutionConfigModel:
        """Validate process execution settings."""
        if self.max_workers is not None and self.max_workers < 1:
            raise ValueError("processes.max_workers must be >= 1 when provided.")
        return self

    def to_dataclass(self) -> ProcessExecutionConfig:
        """Convert the validated model to a dataclass.

        Returns
        -------
        ProcessExecutionConfig
            Dataclass representation.

        """
        return ProcessExecutionConfig(
            enabled=self.enabled,
            max_workers=self.max_workers,
        )


class ParallelExecutionConfigModel(BaseModel):
    """Pydantic model for parallel execution settings."""

    model_config = ConfigDict(extra="forbid")

    threads: ThreadExecutionConfigModel = Field(default_factory=ThreadExecutionConfigModel)
    processes: ProcessExecutionConfigModel = Field(default_factory=ProcessExecutionConfigModel)

    def to_dataclass(self) -> ParallelExecutionConfig:
        """Convert the validated model to a dataclass.

        Returns
        -------
        ParallelExecutionConfig
            Dataclass representation.

        """
        return ParallelExecutionConfig(
            threads=self.threads.to_dataclass(),
            processes=self.processes.to_dataclass(),
        )


class ExecutionConfigModel(BaseModel):
    """Pydantic model for execution settings."""

    model_config = ConfigDict(extra="forbid")

    parallel: ParallelExecutionConfigModel = Field(default_factory=ParallelExecutionConfigModel)

    def to_dataclass(self) -> ExecutionConfig:
        """Convert the validated model to a dataclass.

        Returns
        -------
        ExecutionConfig
            Dataclass representation.

        """
        return ExecutionConfig(parallel=self.parallel.to_dataclass())


class GlobalConfigModel(BaseModel):
    """Pydantic model for top-level config validation."""

    model_config = ConfigDict(extra="ignore")

    env: str
    logging: LoggingConfigModel
    execution: ExecutionConfigModel = Field(default_factory=ExecutionConfigModel)
    inputs: dict[str, IOConfigModel] = Field(default_factory=dict)
    active_domains: list[str] = Field(default_factory=list)
    active_tags: list[TagType] = Field(default_factory=list)
    domains: dict[str, DomainConfigModel] = Field(default_factory=dict)

    @model_validator(mode="after")
    def resolve_domain_inputs(self) -> GlobalConfigModel:
        """Resolve domain input names to global input configs."""
        global_inputs = self.inputs
        for domain_name, domain in self.domains.items():
            if isinstance(domain.inputs, list):
                missing = [name for name in domain.inputs if name not in global_inputs]
                if missing:
                    missing_list = ", ".join(missing)
                    raise ValueError(f"Domain '{domain_name}' references unknown inputs: {missing_list}")
                domain.inputs = {name: global_inputs[name] for name in domain.inputs}
        return self

    @model_validator(mode="after")
    def validate_active_domains(self) -> GlobalConfigModel:
        """Validate that active_domains only reference implemented domains."""
        available = set(self.domains.keys())
        invalid = [d for d in self.active_domains if d not in available]
        if invalid:
            invalid_list = ", ".join(invalid)
            available_list = ", ".join(sorted(available)) if available else "none"
            raise ValueError(
                f"active_domains references unknown domains: {invalid_list}. "
                f"Available domains: {available_list}."
            )
        return self

    def to_dataclass(self) -> GlobalConfig:
        """Convert the validated model to a dataclass.

        Returns
        -------
        GlobalConfig
            Dataclass representation.

        """
        return GlobalConfig(
            env=self.env,
            logging=self.logging.to_dataclass(),
            execution=self.execution.to_dataclass(),
            inputs={key: value.to_dataclass() for key, value in self.inputs.items()},
            active_domains=list(self.active_domains),
            active_tags=list(self.active_tags),
            domains={key: value.to_dataclass() for key, value in self.domains.items()},
        )
