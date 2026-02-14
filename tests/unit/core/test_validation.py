"""Tests for config validation."""

from __future__ import annotations

import pytest
from omegaconf import OmegaConf

from insert_package_name.core.errors import ConfigValidationError
from insert_package_name.core.validation import load_and_validate_config


def test_load_and_validate_config_success(valid_config_dict) -> None:
    cfg = OmegaConf.create(valid_config_dict)

    app_cfg = load_and_validate_config(cfg)
    assert app_cfg.env == "dev"
    assert app_cfg.logging.level == "INFO"


def test_load_and_validate_config_failure() -> None:
    cfg = OmegaConf.create({"logging": {"level": "INFO"}})

    with pytest.raises(ConfigValidationError):
        load_and_validate_config(cfg)
