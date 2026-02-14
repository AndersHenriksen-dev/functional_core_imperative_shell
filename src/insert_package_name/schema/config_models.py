"""Pydantic models for configuration validation."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator

from insert_package_name.schema.types import (
    DomainConfig,
    FileFormat,
    GlobalConfig,
    IOConfig,
    LoggingConfig,
    ScheduleConfig,
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


class GlobalConfigModel(BaseModel):
    """Pydantic model for top-level config validation."""

    model_config = ConfigDict(extra="ignore")

    env: str
    logging: LoggingConfigModel
    inputs: dict[str, IOConfigModel] = Field(default_factory=dict)
    active_domains: list[str] = Field(default_factory=list)
    active_tags: list[str] = Field(default_factory=list)
    domains: dict[str, DomainConfigModel] = Field(default_factory=dict)

    @model_validator(mode="after")
    def resolve_domain_inputs(self) -> "GlobalConfigModel":
        """Resolve domain input names to global input configs."""
        global_inputs = self.inputs
        for domain_name, domain in self.domains.items():
            if isinstance(domain.inputs, list):
                missing = [name for name in domain.inputs if name not in global_inputs]
                if missing:
                    missing_list = ", ".join(missing)
                    raise ValueError(
                        f"Domain '{domain_name}' references unknown inputs: {missing_list}"
                    )
                domain.inputs = {name: global_inputs[name] for name in domain.inputs}
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
            inputs={key: value.to_dataclass() for key, value in self.inputs.items()},
            active_domains=list(self.active_domains),
            active_tags=list(self.active_tags),
            domains={key: value.to_dataclass() for key, value in self.domains.items()},
        )
