"""Scheduler entry point for domain execution on schedules."""

from __future__ import annotations

import hydra
from omegaconf import DictConfig

from insert_package_name.core.logging import configure_logging, get_logger
from insert_package_name.core.scheduler import schedule_domains
from insert_package_name.core.validation import load_and_validate_config

logger = get_logger(__name__)


@hydra.main(version_base=None, config_path="pkg://insert_package_name.configs", config_name="config")
def main(cfg: DictConfig) -> None:
    """Run an APScheduler-based scheduler for configured domains.

    Domain schedules are defined in domain configs with:
    - enabled: true
    - interval: "daily" | "weekly" | "monthly"
    - hour: 0-23
    - minute: 0-59
    - day_of_week: "monday" - "sunday" (for weekly)
    - day_of_month: 1-31 (for monthly)

    Or use cron expression directly:
    - cron: "0 2 * * *"  # 2am daily

    Parameters
    ----------
    cfg : DictConfig
        Hydra configuration loaded from configs/.

    Raises
    ------
    ConfigValidationError
        If configuration is invalid.
    ValueError
        If no domains are scheduled.

    """
    global_config = load_and_validate_config(cfg)
    configure_logging(global_config.logging)

    scheduler = schedule_domains(global_config)

    logger.info("Scheduler is running. Press Ctrl+C to exit.")
    try:
        scheduler.start()
        scheduler._scheduler.wait()  # pylint: disable=protected-access
    except KeyboardInterrupt:
        logger.info("Scheduler interrupted by user")
        scheduler.shutdown()


if __name__ == "__main__":
    main()
