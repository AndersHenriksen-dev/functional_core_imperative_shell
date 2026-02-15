"""Hydra entry point for orchestrating domains."""

from __future__ import annotations

import sys
import traceback
from pathlib import Path
from typing import Any

import hydra
from hydra import compose, initialize_config_dir
from hydra.core.global_hydra import GlobalHydra
from omegaconf import DictConfig, OmegaConf

import insert_package_name.configs
from insert_package_name.core.logging import configure_logging, get_logger
from insert_package_name.core.orchestrator import run_domains_safe
from insert_package_name.core.validation import load_and_validate_config

# Custom Resolvers
OmegaConf.register_new_resolver("min", lambda x, y: min(int(x), int(y)), replace=True)
OmegaConf.register_new_resolver("div_round", lambda x, y: max(1, int(x) // int(y)), replace=True)


def get_config_directory() -> str:
    """Resolve the absolute path to the configuration directory."""
    return str(Path(insert_package_name.configs.__file__).parent)


def load_domain_configs(domains_to_load: list[str], cli_overrides: list[str], logger: Any):
    """Load and validate configs iteratively for a list of domains."""
    valid_configs = []
    failed_domains = []

    for domain_name in domains_to_load:
        try:
            domain_overrides = [*cli_overrides, f"+domain={domain_name}"]
            domain_cfg = compose(config_name="config", overrides=domain_overrides)
            validated = load_and_validate_config(domain_cfg)

            if domain_name in validated.domains:
                valid_configs.append((domain_name, validated))
                logger.info(f"[OK] Successfully loaded: {domain_name}")
            else:
                logger.warning(f"[SKIP] Domain '{domain_name}' not found in config")
                failed_domains.append(domain_name)
        except Exception as exc:
            logger.error(f"[FAIL] Failed to load '{domain_name}': {exc}")
            logger.debug(traceback.format_exc())
            failed_domains.append(domain_name)

    return valid_configs, failed_domains


@hydra.main(version_base=None, config_path="pkg://insert_package_name.configs", config_name="config")
def main(cfg: DictConfig) -> None:
    """Orchestrator entry point."""
    cli_overrides = sys.argv[1:] if len(sys.argv) > 1 else []
    GlobalHydra.instance().clear()
    logger = None

    try:
        with initialize_config_dir(version_base=None, config_dir=get_config_directory()):
            # 1. Initial Setup & Logging
            schedule_cfg = compose(config_name="config", overrides=cli_overrides)
            temp_cfg = load_and_validate_config(schedule_cfg)
            configure_logging(temp_cfg.logging)
            logger = get_logger("orchestrator")

            # 2. Identify Domains
            domains_to_load = schedule_cfg.get("domains_to_run") or list(schedule_cfg.get("domains", {}).keys())
            logger.info(f"Attempting to load {len(domains_to_load)} domain(s)")

            # 3. Load & Validate
            valid_configs, failed_domains = load_domain_configs(domains_to_load, cli_overrides, logger)

            # 4. Final Execution
            if not valid_configs:
                logger.error("No valid configurations. Exiting.")
                return

            if failed_domains:
                logger.warning(f"The following domains will NOT run: {failed_domains}")

            run_domains_safe(temp_cfg, allowed_domains={name for name, _ in valid_configs})

    except Exception as exc:
        if logger:
            logger.error(f"Orchestration failed: {exc}", exc_info=True)
        else:
            print(f"Fatal setup error: {exc}", file=sys.stderr)
            traceback.print_exc()
        raise


if __name__ == "__main__":
    main()
