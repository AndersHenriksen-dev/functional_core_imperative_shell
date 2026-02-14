"""Tests for scheduling functionality."""

from __future__ import annotations

from apscheduler.triggers.cron import CronTrigger

from insert_package_name.core.scheduler import _get_cron_trigger
from insert_package_name.schema.types import DomainConfig, GlobalConfig, LoggingConfig, ScheduleConfig


def test_daily_cron_trigger() -> None:
    """Test daily schedule creates correct cron trigger."""
    schedule = ScheduleConfig(enabled=True, interval="daily", hour=2, minute=30)
    domain = DomainConfig(
        name="test_domain",
        schedule=schedule,
    )
    global_cfg = GlobalConfig(
        env="test",
        logging=LoggingConfig(),
        domains={"test_domain": domain},
    )

    trigger = _get_cron_trigger("test_domain", global_cfg)
    assert trigger is not None
    assert isinstance(trigger, CronTrigger)


def test_weekly_cron_trigger() -> None:
    """Test weekly schedule creates correct cron trigger."""
    schedule = ScheduleConfig(
        enabled=True,
        interval="weekly",
        day_of_week="monday",
        hour=9,
        minute=0,
    )
    domain = DomainConfig(
        name="test_domain",
        schedule=schedule,
    )
    global_cfg = GlobalConfig(
        env="test",
        logging=LoggingConfig(),
        domains={"test_domain": domain},
    )

    trigger = _get_cron_trigger("test_domain", global_cfg)
    assert trigger is not None
    assert isinstance(trigger, CronTrigger)


def test_monthly_cron_trigger() -> None:
    """Test monthly schedule creates correct cron trigger."""
    schedule = ScheduleConfig(
        enabled=True,
        interval="monthly",
        day_of_month=15,
        hour=3,
        minute=0,
    )
    domain = DomainConfig(
        name="test_domain",
        schedule=schedule,
    )
    global_cfg = GlobalConfig(
        env="test",
        logging=LoggingConfig(),
        domains={"test_domain": domain},
    )

    trigger = _get_cron_trigger("test_domain", global_cfg)
    assert trigger is not None
    assert isinstance(trigger, CronTrigger)


def test_cron_expression() -> None:
    """Test explicit cron expression."""
    schedule = ScheduleConfig(enabled=True, cron="0 2 * * *")
    domain = DomainConfig(
        name="test_domain",
        schedule=schedule,
    )
    global_cfg = GlobalConfig(
        env="test",
        logging=LoggingConfig(),
        domains={"test_domain": domain},
    )

    trigger = _get_cron_trigger("test_domain", global_cfg)
    assert trigger is not None
    assert isinstance(trigger, CronTrigger)


def test_disabled_schedule() -> None:
    """Test that disabled schedules return None."""
    schedule = ScheduleConfig(enabled=False, interval="daily")
    domain = DomainConfig(
        name="test_domain",
        schedule=schedule,
    )
    global_cfg = GlobalConfig(
        env="test",
        logging=LoggingConfig(),
        domains={"test_domain": domain},
    )

    trigger = _get_cron_trigger("test_domain", global_cfg)
    assert trigger is None


def test_missing_domain() -> None:
    """Test that missing domains return None."""
    global_cfg = GlobalConfig(
        env="test",
        logging=LoggingConfig(),
        domains={},
    )

    trigger = _get_cron_trigger("nonexistent", global_cfg)
    assert trigger is None
