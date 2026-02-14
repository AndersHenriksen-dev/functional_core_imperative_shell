"""Domain scheduling and execution."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from insert_package_name.core.orchestrator import run_domains_safe
from insert_package_name.schema.types import GlobalConfig

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)


def _get_cron_trigger(domain_name: str, global_cfg: GlobalConfig) -> CronTrigger | None:
    """Generate a cron trigger from domain schedule config.

    Parameters
    ----------
    domain_name : str
        Name of the domain.
    global_cfg : GlobalConfig
        Global configuration.

    Returns
    -------
    CronTrigger | None
        Cron trigger if schedule is configured, otherwise None.

    """
    domain = global_cfg.domains.get(domain_name)
    if not domain or not domain.schedule.enabled:
        return None

    sched = domain.schedule

    # If explicit cron expression is provided, use it
    if sched.cron:
        return CronTrigger.from_crontab(sched.cron)

    # Otherwise, build from interval
    if sched.interval == "daily":
        return CronTrigger(hour=sched.hour, minute=sched.minute)
    elif sched.interval == "weekly":
        day_map = {
            "monday": 0,
            "tuesday": 1,
            "wednesday": 2,
            "thursday": 3,
            "friday": 4,
            "saturday": 5,
            "sunday": 6,
        }
        day_num = day_map.get(sched.day_of_week.lower(), 0)
        return CronTrigger(day_of_week=day_num, hour=sched.hour, minute=sched.minute)
    elif sched.interval == "monthly":
        return CronTrigger(day=sched.day_of_month, hour=sched.hour, minute=sched.minute)

    return None


def schedule_domains(global_cfg: GlobalConfig) -> BackgroundScheduler:
    """Create a scheduler for configured domains.

    Parameters
    ----------
    global_cfg : GlobalConfig
        Global application configuration.

    Returns
    -------
    BackgroundScheduler
        Running scheduler instance.

    Raises
    ------
    ValueError
        If no domains are scheduled.

    """
    scheduler = BackgroundScheduler()

    scheduled_count = 0
    for domain_name in global_cfg.domains:
        trigger = _get_cron_trigger(domain_name, global_cfg)
        if trigger:
            scheduler.add_job(
                run_domains_safe,
                trigger,
                args=[global_cfg],
                kwargs={"allowed_domains": {domain_name}},
                id=f"domain_{domain_name}",
                name=f"Domain: {global_cfg.domains[domain_name].name}",
                misfire_grace_time=60,
                coalesce=True,
            )
            logger.info(f"Scheduled domain '{domain_name}' with trigger: {trigger}")
            scheduled_count += 1

    if scheduled_count == 0:
        msg = "No domains with schedules enabled found in config"
        raise ValueError(msg)

    logger.info(f"Scheduler configured with {scheduled_count} scheduled domain(s)")

    return scheduler
