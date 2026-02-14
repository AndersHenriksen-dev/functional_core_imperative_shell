"""Tests for schema and config models."""

from __future__ import annotations

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
