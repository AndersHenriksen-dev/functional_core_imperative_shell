"""Tests for schema types and dataclasses."""

from __future__ import annotations

from dataclasses import fields

import pytest

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


class TestIOConfig:
    """Test IOConfig dataclass."""

    def test_io_config_creation(self):
        """Test creating IOConfig with valid parameters."""
        config = IOConfig(
            path="/data/file.csv", format=FileFormat.CSV, options={"sep": ","}, storage_options={"key": "value"}
        )

        assert config.path == "/data/file.csv"
        assert config.format == FileFormat.CSV
        assert config.options == {"sep": ","}
        assert config.storage_options == {"key": "value"}

    def test_io_config_defaults(self):
        """Test IOConfig with default values."""
        config = IOConfig(path="/data/file.csv", format=FileFormat.CSV)

        assert config.path == "/data/file.csv"
        assert config.format == FileFormat.CSV
        assert config.options == {}
        assert config.storage_options == {}

    def test_io_config_immutable(self):
        """Test that IOConfig is immutable (frozen dataclass)."""
        config = IOConfig(path="/data/file.csv", format=FileFormat.CSV)

        with pytest.raises(AttributeError):
            config.path = "/new/path"


class TestLoggingConfig:
    """Test LoggingConfig dataclass."""

    def test_logging_config_creation(self):
        """Test creating LoggingConfig with valid parameters."""
        config = LoggingConfig(level="INFO", log_dir="/logs", to_console=True, to_file=True)

        assert config.level == "INFO"
        assert config.log_dir == "/logs"
        assert config.to_console is True
        assert config.to_file is True

    def test_logging_config_defaults(self):
        """Test LoggingConfig with default values."""
        config = LoggingConfig(level="DEBUG", log_dir="/logs")

        assert config.level == "DEBUG"
        assert config.log_dir == "/logs"
        assert config.to_console is True
        assert config.to_file is True


class TestExecutionConfig:
    """Test ExecutionConfig dataclass."""

    def test_execution_config_creation(self):
        """Test creating ExecutionConfig with valid parameters."""
        parallel_config = ParallelExecutionConfig(
            threads=ThreadExecutionConfig(enabled=True, max_workers=4),
            processes=ProcessExecutionConfig(enabled=False, max_workers=2),
        )

        config = ExecutionConfig(parallel=parallel_config)

        assert config.parallel.threads.enabled is True
        assert config.parallel.threads.max_workers == 4
        assert config.parallel.processes.enabled is False
        assert config.parallel.processes.max_workers == 2


class TestDomainConfig:
    """Test DomainConfig dataclass."""

    def test_domain_config_creation(self):
        """Test creating DomainConfig with valid parameters."""
        inputs = {
            "customers": IOConfig(path="/data/customers.csv", format=FileFormat.CSV),
            "transactions": IOConfig(path="/data/transactions.csv", format=FileFormat.CSV),
        }

        outputs = {
            "scores": IOConfig(path="/output/scores.csv", format=FileFormat.CSV),
            "metrics": IOConfig(path="/output/metrics.csv", format=FileFormat.CSV),
        }

        config = DomainConfig(
            name="test_domain", enabled=True, tags=["daily"], inputs=inputs, params={"threshold": 0.7}, outputs=outputs
        )

        assert config.name == "test_domain"
        assert config.enabled is True
        assert config.tags == ["daily"]
        assert len(config.inputs) == 2
        assert config.params == {"threshold": 0.7}
        assert len(config.outputs) == 2


class TestGlobalConfig:
    """Test GlobalConfig dataclass."""

    def test_global_config_creation(self):
        """Test creating GlobalConfig with valid parameters."""
        logging_config = LoggingConfig(level="INFO", log_dir="/logs")
        execution_config = ExecutionConfig()

        inputs = {"customers": IOConfig(path="/data/customers.csv", format=FileFormat.CSV)}

        domains = {
            "test_domain": DomainConfig(
                name="test_domain", enabled=True, tags=["daily"], inputs={}, params={}, outputs={}
            )
        }

        config = GlobalConfig(
            env="dev",
            logging=logging_config,
            execution=execution_config,
            inputs=inputs,
            active_domains=["test_domain"],
            active_tags=["daily"],
            domains=domains,
        )

        assert config.env == "dev"
        assert config.logging.level == "INFO"
        assert len(config.inputs) == 1
        assert config.active_domains == ["test_domain"]
        assert config.active_tags == ["daily"]
        assert len(config.domains) == 1

    def test_global_config_with_run_domains(self):
        """Test GlobalConfig with run_domains parameter."""
        # Note: run_domains is not in the current GlobalConfig implementation
        # This test is for future compatibility
        pass


class TestScheduleConfig:
    """Test ScheduleConfig dataclass."""

    def test_schedule_config_creation(self):
        """Test creating ScheduleConfig with valid parameters."""
        config = ScheduleConfig(enabled=True, interval="daily", hour=2, minute=30)

        assert config.enabled is True
        assert config.interval == "daily"
        assert config.hour == 2
        assert config.minute == 30
        assert config.cron == ""  # Default empty string

    def test_schedule_config_with_cron(self):
        """Test ScheduleConfig with cron expression."""
        config = ScheduleConfig(enabled=True, cron="0 2 * * *")

        assert config.enabled is True
        assert config.cron == "0 2 * * *"
        assert config.interval == ""  # Default empty string


class TestEnums:
    """Test enum types."""

    def test_file_format_enum(self):
        """Test FileFormat enum values."""
        assert FileFormat.CSV == "csv"
        assert FileFormat.PARQUET == "parquet"
        assert FileFormat.JSON == "json"
        assert FileFormat.EXCEL == "excel"
        assert FileFormat.FEATHER == "feather"
        assert FileFormat.ORC == "orc"
        assert FileFormat.PICKLE == "pickle"
        assert FileFormat.SQL == "sql"
        assert FileFormat.DELTA == "delta"

    def test_tag_type_literal(self):
        """Test TagType literal values."""
        # TagType is a Literal, so we test valid values
        from typing import get_args

        tag_args = get_args(TagType)
        assert "daily" in tag_args
        assert "monthly" in tag_args
        assert "all" in tag_args
        assert None in tag_args


class TestDataclassImmutability:
    """Test that all dataclasses are properly frozen."""

    def test_all_dataclasses_frozen(self):
        """Test that all dataclasses are frozen (immutable)."""
        dataclass_types = [
            IOConfig,
            LoggingConfig,
            ExecutionConfig,
            DomainConfig,
            GlobalConfig,
            ScheduleConfig,
            ProcessExecutionConfig,
            ThreadExecutionConfig,
            ParallelExecutionConfig,
        ]

        for dataclass_type in dataclass_types:
            # Create instance with minimal required fields
            if dataclass_type == IOConfig:
                instance = dataclass_type(path="/test", format=FileFormat.CSV)
            elif dataclass_type == LoggingConfig:
                instance = dataclass_type(level="INFO", log_dir="/logs")
            elif dataclass_type == ExecutionConfig:
                instance = dataclass_type()
            elif dataclass_type == DomainConfig:
                instance = dataclass_type(name="test", enabled=True, tags=[], inputs={}, params={}, outputs={})
            elif dataclass_type == GlobalConfig:
                instance = dataclass_type(
                    env="dev",
                    logging=LoggingConfig(level="INFO", log_dir="/logs"),
                    execution=ExecutionConfig(),
                    inputs={},
                    active_domains=[],
                    active_tags=[],
                    domains={},
                )
            elif dataclass_type == ScheduleConfig:
                instance = dataclass_type(enabled=True, interval="daily")
            elif dataclass_type in [ProcessExecutionConfig, ThreadExecutionConfig]:
                instance = dataclass_type(enabled=False, max_workers=1)
            elif dataclass_type == ParallelExecutionConfig:
                instance = dataclass_type()

            # Check that it's frozen
            assert instance.__dataclass_params__.frozen

            # Try to modify a field (should fail)
            field_names = [f.name for f in fields(instance)]
            if field_names:
                first_field = field_names[0]
                with pytest.raises(AttributeError):
                    setattr(instance, first_field, "new_value")
