"""Hydra config validation and conversion."""

from __future__ import annotations

from omegaconf import DictConfig, OmegaConf
from pydantic import ValidationError

from insert_package_name.core.errors import ConfigValidationError
from insert_package_name.schema.config_models import GlobalConfigModel
from insert_package_name.schema.types import GlobalConfig


def load_and_validate_config(cfg: DictConfig) -> GlobalConfig:
    """Convert Hydra config to validated dataclasses.

    Parameters
    ----------
    cfg : DictConfig
        Hydra config object.

    Returns
    -------
    GlobalConfig
        Validated configuration as dataclasses.

    Raises
    ------
    ConfigValidationError
        If Pydantic validation fails.

    """
    raw = OmegaConf.to_container(cfg, resolve=True)
    try:
        model = GlobalConfigModel.model_validate(raw)
    except ValidationError as exc:
        raise ConfigValidationError("Configuration validation failed.", details=exc.errors()) from exc
    return model.to_dataclass()
