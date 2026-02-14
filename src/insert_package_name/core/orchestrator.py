"""Orchestration for running domain pipelines."""

from __future__ import annotations

import importlib
from collections.abc import Iterable

from insert_package_name.core.errors import (
    DataHandlingError,
    DomainExecutionError,
    DomainInterfaceError,
    DomainNotFoundError,
)
from insert_package_name.core.logging import get_domain_logger
from insert_package_name.schema.types import DomainConfig, GlobalConfig


def _load_domain_runner(domain_name: str):
    """Import a domain module and return its run function.

    Parameters
    ----------
    domain_name : str
        Domain module name under insert_package_name.domains.

    Returns
    -------
    Callable
        Domain run function.

    Raises
    ------
    DomainNotFoundError
        If the domain module cannot be imported.
    DomainInterfaceError
        If the module does not expose a run function.

    """
    try:
        module = importlib.import_module(f"insert_package_name.domains.{domain_name}.pipeline")
    except ModuleNotFoundError as exc:
        msg = "Domain pipeline module not found"
        raise DomainNotFoundError(domain=domain_name, message=msg) from exc

    if not hasattr(module, "run"):
        msg = "Domain module is missing required 'run' function"
        raise DomainInterfaceError(domain=domain_name, message=msg)
    return module.run


def _iter_selected_domains(cfg: GlobalConfig, allowed_domains: set[str] | None = None) -> Iterable[tuple[str, DomainConfig]]:
    """Yield domain configs that match active filters.

    Parameters
    ----------
    cfg : GlobalConfig
        Global configuration with domains and filters.
    allowed_domains : set[str] | None
        If provided, only yield domains in this set.

    Returns
    -------
    Iterable[tuple[str, DomainConfig]]
        Domain names paired with their configs.

    """
    selected = cfg.domains.items()

    if allowed_domains:
        selected = [(name, domain) for name, domain in selected if name in allowed_domains]

    if cfg.active_domains:
        selected = [(name, domain) for name, domain in selected if name in cfg.active_domains]

    if cfg.active_tags:
        selected = [(name, domain) for name, domain in selected if set(cfg.active_tags).intersection(domain.tags)]

    return selected


def run_domains(cfg: GlobalConfig) -> None:
    """Run selected domains based on config filters.

    Parameters
    ----------
    cfg : GlobalConfig
        Global configuration with domains and filters.

    Raises
    ------
    DomainExecutionError
        If a domain fails during execution.
    DataHandlingError
        If a known data handling error is raised.

    """
    for domain_name, domain_cfg in _iter_selected_domains(cfg):
        logger = get_domain_logger("orchestrator", domain_name)

        if not domain_cfg.enabled:
            logger.info("Skipping domain (disabled)")
            continue

        logger.info("Starting domain")
        runner = _load_domain_runner(domain_name)
        try:
            runner(domain_cfg)
        except DataHandlingError:
            raise
        except Exception as exc:
            msg = "Domain execution failed"
            raise DomainExecutionError(domain=domain_name, message=msg) from exc
        logger.info("Completed domain")


def run_domains_safe(cfg: GlobalConfig, allowed_domains: set[str] | None = None) -> None:
    """Run selected domains with individual error isolation.

    Unlike run_domains, this function catches and logs errors for individual domains
    without stopping execution of other domains.

    Parameters
    ----------
    cfg : GlobalConfig
        Global configuration with domains and filters.
    allowed_domains : set[str] | None
        If provided, only run domains in this set.

    """
    for domain_name, domain_cfg in _iter_selected_domains(cfg, allowed_domains):
        logger = get_domain_logger("orchestrator", domain_name)

        if not domain_cfg.enabled:
            logger.info("Skipping domain (disabled)")
            continue

        logger.info("Starting domain")
        try:
            runner = _load_domain_runner(domain_name)
            runner(domain_cfg)
            logger.info("Completed domain")
        except (DomainNotFoundError, DomainInterfaceError) as exc:
            logger.error(f"Domain setup error: {exc}")
        except DataHandlingError as exc:
            logger.error(f"Data handling error: {exc}", exc_info=True)
        except Exception as exc:
            logger.error(f"Unexpected error during domain execution: {exc}", exc_info=True)
