"""Custom exceptions for insert_package_name."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


class DataHandlingError(Exception):
    """Base exception for insert_package_name errors."""

    def __init_subclass__(cls) -> None:
        """Hide module-qualified names in tracebacks for subclasses."""
        super().__init_subclass__()
        cls.__module__ = "builtins"


DataHandlingError.__module__ = "builtins"


@dataclass
class ConfigValidationError(DataHandlingError):
    """Raised when the Hydra configuration fails validation."""

    message: str
    details: Any | None = None

    def __str__(self) -> str:
        """Return a readable error message."""
        if self.details is None:
            return self.message
        return f"{self.message} Details: {self.details}"


@dataclass
class SchemaValidationError(DataHandlingError):
    """Raised when a dataset fails schema validation."""

    message: str
    dataset: str | None = None

    def __str__(self) -> str:
        """Return a readable error message."""
        if self.dataset:
            return f"{self.message} Dataset: {self.dataset}"
        return self.message


@dataclass
class DomainError(DataHandlingError):
    """Base exception for domain-related errors."""

    domain: str
    message: str

    def __str__(self) -> str:
        """Return a readable error message."""
        return f"{self.domain}: {self.message}"


class DomainNotFoundError(DomainError):
    """Raised when a domain module cannot be imported."""


class DomainInterfaceError(DomainError):
    """Raised when a domain does not expose the expected interface."""


class DomainExecutionError(DomainError):
    """Raised when a domain fails during execution."""


@dataclass
class MissingIOKeyError(DataHandlingError):
    """Raised when a domain references an unknown input/output key."""

    domain: str
    key: str
    available_inputs: list[str]
    available_outputs: list[str]

    def __str__(self) -> str:
        """Return a readable error message."""
        inputs = ", ".join(self.available_inputs) if self.available_inputs else "none"
        outputs = ", ".join(self.available_outputs) if self.available_outputs else "none"
        return f"{self.domain}: unknown IO key '{self.key}'. Inputs: {inputs}. Outputs: {outputs}."


@dataclass
class IOBaseError(DataHandlingError):
    """Base exception for IO failures."""

    message: str
    path: str | None = None
    file_format: str | None = None

    def __str__(self) -> str:
        """Return a readable error message."""
        parts = [self.message]
        if self.path:
            parts.append(f"path={self.path}")
        if self.file_format:
            parts.append(f"format={self.file_format}")
        return " | ".join(parts)


class IOConfigError(IOBaseError):
    """Raised when IO configuration is invalid."""


class IOReadError(IOBaseError):
    """Raised when an IO read fails."""


class IOWriteError(IOBaseError):
    """Raised when an IO write fails."""


class UnsupportedFormatError(IOBaseError):
    """Raised when a file format is not supported or registered."""


@dataclass
class OptionalDependencyError(DataHandlingError):
    """Raised when an optional dependency is required but missing."""

    dependency: str
    feature: str

    def __str__(self) -> str:
        """Return a readable error message."""
        return f"Missing optional dependency '{self.dependency}' for {self.feature}."
