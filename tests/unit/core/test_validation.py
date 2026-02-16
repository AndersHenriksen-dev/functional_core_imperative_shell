"""Tests for config validation."""

from __future__ import annotations

from unittest.mock import patch

import pytest
from omegaconf import OmegaConf
from pydantic import ValidationError

from insert_package_name.core.errors import ConfigValidationError
from insert_package_name.core.validation import load_and_validate_config
from insert_package_name.schema.types import GlobalConfig


def test_load_and_validate_config_success(valid_config_dict) -> None:
    cfg = OmegaConf.create(valid_config_dict)

    app_cfg = load_and_validate_config(cfg)
    assert app_cfg.env == "dev"
    assert app_cfg.logging.level == "INFO"


def test_load_and_validate_config_failure() -> None:
    cfg = OmegaConf.create({"logging": {"level": "INFO"}})

    with pytest.raises(ConfigValidationError):
        load_and_validate_config(cfg)


class TestLoadAndValidateConfig:
    """Test load_and_validate_config function."""

    def test_load_and_validate_config_basic(self):
        """Test successful config loading and validation."""
        config_dict = {
            "env": "dev",
            "logging": {"level": "INFO", "log_dir": "/logs", "to_console": True, "to_file": True},
            "execution": {
                "parallel": {
                    "threads": {"enabled": False, "max_workers": 1},
                    "processes": {"enabled": False, "max_workers": 1},
                }
            },
            "inputs": {},
            "active_domains": [],
            "active_tags": [],
            "domains": {},
        }

        cfg = OmegaConf.create(config_dict)

        result = load_and_validate_config(cfg)

        assert isinstance(result, GlobalConfig)
        assert result.env == "dev"
        assert result.logging.level == "INFO"

    def test_load_and_validate_config_validation_error(self):
        """Test config loading with validation error."""
        # Invalid config - missing required fields
        config_dict = {
            "env": "dev",
            # Missing logging, execution, etc.
        }

        cfg = OmegaConf.create(config_dict)

        with pytest.raises(ConfigValidationError, match="Configuration validation failed"):
            load_and_validate_config(cfg)

    def test_load_and_validate_config_pydantic_error(self):
        """Test config loading with Pydantic validation error."""
        config_dict = {
            "env": "dev",
            "logging": {
                "level": "INVALID_LEVEL",  # Invalid log level
                "log_dir": "/logs",
                "to_console": True,
                "to_file": True,
            },
            "execution": {
                "parallel": {
                    "enabled": False,
                    "threads": {"enabled": False, "max_workers": 1},
                    "processes": {"enabled": False, "max_workers": 1},
                }
            },
            "inputs": {},
            "active_domains": [],
            "active_tags": [],
            "domains": {},
        }

        cfg = OmegaConf.create(config_dict)

        with pytest.raises(ConfigValidationError) as exc_info:
            load_and_validate_config(cfg)

        # Check that details are included
        assert exc_info.value.details is not None
        assert len(exc_info.value.details) > 0

    def test_load_and_validate_config_with_run_domains(self):
        """Test config loading with run_domains parameter."""
        config_dict = {
            "env": "dev",
            "logging": {"level": "INFO", "log_dir": "/logs", "to_console": True, "to_file": True},
            "execution": {
                "parallel": {
                    "threads": {"enabled": False, "max_workers": 1},
                    "processes": {"enabled": False, "max_workers": 1},
                }
            },
            "inputs": {},
            "active_domains": [],
            "active_tags": [],
            "domains": {},
            "run_domains": ["domain1", "domain2"],  # Extra field should be ignored
        }

        cfg = OmegaConf.create(config_dict)

        result = load_and_validate_config(cfg)

        assert isinstance(result, GlobalConfig)
        assert result.env == "dev"
        # run_domains is not part of the schema, so it's ignored

    @patch("insert_package_name.schema.config_models.GlobalConfigModel.model_validate")
    def test_load_and_validate_config_model_error(self, mock_validate):
        """Test config loading when model validation fails."""
        mock_validate.side_effect = ValidationError.from_exception_data(title="ValidationError", line_errors=[])

        config_dict = {
            "env": "dev",
            "logging": {"level": "INFO", "log_dir": "/logs", "to_console": True, "to_file": True},
            "execution": {
                "parallel": {
                    "enabled": False,
                    "threads": {"enabled": False, "max_workers": 1},
                    "processes": {"enabled": False, "max_workers": 1},
                }
            },
            "inputs": {},
            "active_domains": [],
            "active_tags": [],
            "domains": {},
        }

        cfg = OmegaConf.create(config_dict)

        with pytest.raises(ConfigValidationError):
            load_and_validate_config(cfg)
