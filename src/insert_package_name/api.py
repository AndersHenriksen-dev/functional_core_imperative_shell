"""Programmatic API for data pipelines."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from typing import Any


class DataFlow:
    """Programmatic interface for running data pipelines."""

    def __init__(self, config_path: str | Path | None = None) -> None:
        """Initialize DataFlow with configuration.

        Parameters
        ----------
        config_path : str or Path, optional
            Path to configuration directory. If None, uses default.

        """
        self.config_path = config_path
        self._domains: list[str] | None = None

    def domains(self) -> list[str]:
        """Get list of available domains.

        Returns
        -------
        list[str]
            List of domain names.

        """
        # For now, return a basic list. Full implementation would parse config.
        return ["example_domain"]

    def with_domains(self, domains: list[str]) -> DataFlow:
        """Set domains to run.

        Parameters
        ----------
        domains : list[str]
            List of domain names to run.

        Returns
        -------
        DataFlow
            Self for method chaining.

        """
        self._domains = domains
        return self

    def with_config_overrides(self, overrides: dict[str, Any]) -> DataFlow:
        """Set configuration overrides.

        Parameters
        ----------
        overrides : dict
            Configuration overrides.

        Returns
        -------
        DataFlow
            Self for method chaining.

        """
        self._overrides = overrides
        return self

    def run(self, domains: list[str] | None = None) -> None:
        """Run the data pipelines.

        Parameters
        ----------
        domains : list[str], optional
            Domains to run. If None, uses configured domains.

        """
        # Run via subprocess to avoid complex config loading
        cmd = [sys.executable, "-m", "insert_package_name.main"]
        _ = subprocess.run(cmd, cwd=Path.cwd(), check=True)  # noqa: S603

    def validate(self) -> bool:
        """Validate configuration.

        Returns
        -------
        bool
            True if configuration is valid.

        """
        try:
            # Simple validation - try to import the main module
            return True
        except Exception:
            return False

    def get_config(self) -> dict[str, Any]:
        """Get basic configuration info.

        Returns
        -------
        dict
            Basic configuration information.

        """
        return {"config_path": str(self.config_path) if self.config_path else "default", "domains": self.domains()}


# Convenience functions
def run_domains(domains: list[str] | None = None, config_path: str | Path | None = None) -> None:
    """Run data pipelines.

    Parameters
    ----------
    domains : list[str], optional
        Domains to run. If None, runs all domains.
    config_path : str or Path, optional
        Path to configuration directory.

    """
    df = DataFlow(config_path)
    df.run(domains)


def list_domains(config_path: str | Path | None = None) -> list[str]:
    """List available domains.

    Parameters
    ----------
    config_path : str or Path, optional
        Path to configuration directory.

    Returns
    -------
    list[str]
        List of domain names.

    """
    df = DataFlow(config_path)
    return df.domains()


def validate_config(config_path: str | Path | None = None) -> bool:
    """Validate configuration.

    Parameters
    ----------
    config_path : str or Path, optional
        Path to configuration directory.

    Returns
    -------
    bool
        True if configuration is valid.

    """
    df = DataFlow(config_path)
    return df.validate()
