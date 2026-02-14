"""Hydra entry point for orchestrating domains."""

from __future__ import annotations

import sys
import traceback

import hydra
from hydra import compose, initialize_config_dir
from hydra.core.global_hydra import GlobalHydra
from omegaconf import DictConfig, OmegaConf

from insert_package_name.core.errors import DataHandlingError
from insert_package_name.core.logging import configure_logging, get_logger
from insert_package_name.core.orchestrator import run_domains_safe
from insert_package_name.core.validation import load_and_validate_config


@hydra.main(version_base=None, config_path="pkg://insert_package_name.configs", config_name="config")
def main(cfg: DictConfig) -> None:
    """Run the configured domains with validated settings.

    Uses iterative safe-loading pattern: each domain config is loaded independently
    with error isolation. Broken domain configs are logged and skipped, allowing
    valid domains to execute successfully.

    Parameters
    ----------
    cfg : DictConfig
        Hydra configuration object.

    """
    # Extract base config and CLI overrides
    base_cfg = OmegaConf.to_container(cfg, resolve=False)
    cli_overrides = sys.argv[1:] if len(sys.argv) > 1 else []

    # Clear Hydra singleton to allow manual composition
    GlobalHydra.instance().clear()

    logger = None
    try:
        # Initialize for manual composition
        from pathlib import Path
        import insert_package_name.configs
        config_dir = str(Path(insert_package_name.configs.__file__).parent)

        with initialize_config_dir(version_base=None, config_dir=config_dir):
            # Get list of domains to attempt loading
            schedule_cfg = compose(config_name="config", overrides=cli_overrides)
            
            # Configure logging early
            temp_cfg = load_and_validate_config(schedule_cfg)
            configure_logging(temp_cfg.logging)
            logger = get_logger("orchestrator")
            logger.info("Starting orchestration with safe-loading pattern")

            # Determine which domains to load
            domains_to_load = schedule_cfg.get("domains_to_run", [])
            if not domains_to_load:
                # Fallback: load from defaults if no explicit list
                domains_to_load = list(schedule_cfg.get("domains", {}).keys())

            logger.info(f"Attempting to load {len(domains_to_load)} domain(s): {domains_to_load}")

            valid_configs = []
            failed_domains = []

            # Iteratively load each domain with error isolation
            for domain_name in domains_to_load:
                try:
                    domain_overrides = cli_overrides + [f"+domain={domain_name}"]
                    domain_cfg = compose(config_name="config", overrides=domain_overrides)
                    
                    # Validate this specific domain config
                    validated = load_and_validate_config(domain_cfg)
                    
                    # Check if domain exists and is parseable
                    if domain_name in validated.domains:
                        valid_configs.append((domain_name, validated))
                        logger.info(f"[OK] Successfully loaded config for domain: {domain_name}")
                    else:
                        logger.warning(f"[SKIP] Domain '{domain_name}' not found in config")
                        failed_domains.append(domain_name)

                except Exception as exc:
                    logger.error(f"[FAIL] Failed to load config for domain '{domain_name}': {exc}")
                    logger.debug(traceback.format_exc())
                    failed_domains.append(domain_name)

            # Summary
            logger.info(f"Config loading complete: {len(valid_configs)} valid, {len(failed_domains)} failed")
            if failed_domains:
                logger.warning(f"The following domains will NOT run: {failed_domains}")

            if not valid_configs:
                logger.error("No valid domain configurations loaded. Exiting.")
                return

            # Execute valid domains
            for domain_name, validated_cfg in valid_configs:
                # Filter to only run this specific domain
                filtered_cfg = validated_cfg
                try:
                    run_domains_safe(filtered_cfg, allowed_domains={domain_name})
                except DataHandlingError as exc:
                    logger.error(f"Domain '{domain_name}' execution failed: {exc}", exc_info=True)
                except Exception as exc:
                    logger.error(f"Unexpected error in domain '{domain_name}': {exc}", exc_info=True)

    except Exception as exc:
        if logger:
            logger.error(f"Orchestration failed: {exc}", exc_info=True)
        else:
            print(f"Fatal error during orchestration setup: {exc}", file=sys.stderr)
            traceback.print_exc()
        raise


if __name__ == "__main__":
    main()
