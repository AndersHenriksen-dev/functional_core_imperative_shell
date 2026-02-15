"""Tests for schema and config models."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from insert_package_name.schema.config_models import GlobalConfigModel
from insert_package_name.schema.types import FileFormat


def test_global_config_model_to_dataclass(valid_config_dict) -> None:
    config = {
        **valid_config_dict,
        "domains": {
            "example": {
                "name": "Example",
                "inputs": {
                    "customers": {"path": "data.csv", "format": FileFormat.CSV},
                },
                "outputs": {
                    "scores": {"path": "scores.csv", "format": FileFormat.CSV},
                },
            }
        },
    }

    model = GlobalConfigModel.model_validate(config)

    dataclass_cfg = model.to_dataclass()
    assert dataclass_cfg.env == "dev"
    assert "example" in dataclass_cfg.domains
    assert dataclass_cfg.domains["example"].inputs["customers"].format is FileFormat.CSV


def test_active_domains_valid(valid_config_dict) -> None:
    """Test that valid active_domains are accepted."""
    config = {
        **valid_config_dict,
        "domains": {
            "example": {
                "name": "Example",
                "inputs": {
                    "customers": {"path": "data.csv", "format": FileFormat.CSV},
                },
                "outputs": {
                    "scores": {"path": "scores.csv", "format": FileFormat.CSV},
                },
            },
            "other": {
                "name": "Other",
                "inputs": {},
                "outputs": {},
            },
        },
        "active_domains": ["example", "other"],
    }

    model = GlobalConfigModel.model_validate(config)
    assert model.active_domains == ["example", "other"]


def test_active_domains_invalid(valid_config_dict) -> None:
    """Test that invalid active_domains raise a validation error."""
    config = {
        **valid_config_dict,
        "domains": {
            "example": {
                "name": "Example",
                "inputs": {},
                "outputs": {},
            }
        },
        "active_domains": ["example", "nonexistent"],
    }

    with pytest.raises(ValidationError) as exc_info:
        GlobalConfigModel.model_validate(config)

    error_msg = str(exc_info.value)
    assert "unknown domains" in error_msg
    assert "nonexistent" in error_msg
    assert "example" in error_msg


def test_domain_inputs_list_valid(valid_config_dict) -> None:
    """Test that domain inputs as a list resolve correctly from global inputs."""
    config = {
        **valid_config_dict,
        "inputs": {
            "customers": {"path": "customers.csv", "format": FileFormat.CSV},
            "transactions": {"path": "transactions.csv", "format": FileFormat.CSV},
        },
        "domains": {
            "example": {
                "name": "Example",
                "inputs": ["customers", "transactions"],
                "outputs": {
                    "scores": {"path": "scores.csv", "format": FileFormat.CSV},
                },
            }
        },
    }

    model = GlobalConfigModel.model_validate(config)
    assert isinstance(model.domains["example"].inputs, dict)
    assert "customers" in model.domains["example"].inputs
    assert "transactions" in model.domains["example"].inputs


def test_domain_inputs_list_invalid(valid_config_dict) -> None:
    """Test that domain inputs list with non-existent inputs raises validation error."""
    config = {
        **valid_config_dict,
        "inputs": {
            "customers": {"path": "customers.csv", "format": FileFormat.CSV},
        },
        "domains": {
            "example": {
                "name": "Example",
                "inputs": ["customers", "nonexistent_input"],
                "outputs": {
                    "scores": {"path": "scores.csv", "format": FileFormat.CSV},
                },
            }
        },
    }

    with pytest.raises(ValidationError) as exc_info:
        GlobalConfigModel.model_validate(config)

    error_msg = str(exc_info.value)
    assert "unknown inputs" in error_msg
    assert "nonexistent_input" in error_msg
