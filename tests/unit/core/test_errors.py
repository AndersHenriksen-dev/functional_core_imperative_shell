"""Tests for custom error types."""

from __future__ import annotations

from insert_package_name.core.errors import (
    ConfigValidationError,
    DomainExecutionError,
    IOReadError,
    OptionalDependencyError,
    SchemaValidationError,
)


def test_config_validation_error_str() -> None:
    error = ConfigValidationError("Invalid config", details={"field": "missing"})
    assert "Invalid config" in str(error)
    assert "field" in str(error)


def test_schema_validation_error_str() -> None:
    error = SchemaValidationError("Schema failed", dataset="customers")
    assert str(error) == "Schema failed Dataset: customers"


def test_domain_error_str() -> None:
    error = DomainExecutionError(domain="example", message="failed")
    assert str(error) == "example: failed"


def test_io_error_str() -> None:
    error = IOReadError(message="read failed", path="/tmp/data.csv", file_format="csv")
    assert "read failed" in str(error)
    assert "path=/tmp/data.csv" in str(error)
    assert "format=csv" in str(error)


def test_optional_dependency_error_str() -> None:
    error = OptionalDependencyError(dependency="deltalake", feature="Delta IO")
    assert "deltalake" in str(error)
