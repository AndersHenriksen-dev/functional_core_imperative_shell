"""Shared pytest fixtures for insert_package_name tests."""

from __future__ import annotations

from collections.abc import Callable

import pandas as pd
import pytest

from insert_package_name.schema.types import DomainConfig, FileFormat, GlobalConfig, IOConfig, LoggingConfig


@pytest.fixture
def customers_df() -> pd.DataFrame:
    """Sample customers dataframe for tests."""
    return pd.DataFrame(
        {
            "customer_id": [1, 2],
            "age": [30, 40],
            "country": ["US", "DK"],
        }
    )


@pytest.fixture
def transactions_df() -> pd.DataFrame:
    """Sample transactions dataframe for tests."""
    return pd.DataFrame(
        {
            "customer_id": [1, 1, 2],
            "amount": [100.0, 50.0, 0.0],
        }
    )


@pytest.fixture
def simple_df() -> pd.DataFrame:
    """Small dataframe used for IO roundtrip tests."""
    return pd.DataFrame({"a": [1, 2], "b": ["x", "y"]})


@pytest.fixture
def example_domain_config() -> DomainConfig:
    """Return an example domain configuration."""
    return DomainConfig(
        name="Example Domain",
        inputs={
            "customers": IOConfig(path="customers.csv", format=FileFormat.CSV),
            "transactions": IOConfig(path="transactions.csv", format=FileFormat.CSV),
        },
        outputs={
            "scores": IOConfig(path="scores.csv", format=FileFormat.CSV),
            "metrics": IOConfig(path="metrics.csv", format=FileFormat.CSV),
        },
        params={"score_threshold": 0.4},
    )


@pytest.fixture
def global_config_factory() -> Callable[[dict[str, DomainConfig], list[str], list[str]], GlobalConfig]:
    """Build GlobalConfig values for tests."""

    def _factory(
        domains: dict[str, DomainConfig],
        active_domains: list[str] | None = None,
        active_tags: list[str] | None = None,
    ) -> GlobalConfig:
        """Create a GlobalConfig using the provided domain settings."""
        return GlobalConfig(
            env="dev",
            logging=LoggingConfig(),
            domains=domains,
            active_domains=active_domains or [],
            active_tags=active_tags or [],
        )

    return _factory


@pytest.fixture
def valid_config_dict() -> dict[str, object]:
    """Hydra-like config dictionary used in validation tests."""
    return {
        "env": "dev",
        "logging": {
            "level": "INFO",
            "log_dir": "logs",
            "to_console": True,
            "to_file": False,
        },
        "active_domains": [],
        "active_tags": [],
        "domains": {},
    }
