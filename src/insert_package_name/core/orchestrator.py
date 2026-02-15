"""Orchestration for running domain pipelines."""

from __future__ import annotations

import importlib
import math
import os
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from collections.abc import Iterable

from insert_package_name.core.errors import (
    DataHandlingError,
    DomainExecutionError,
    DomainInterfaceError,
    DomainNotFoundError,
    MissingIOKeyError,
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


def _missing_io_key_error(domain_name: str, domain_cfg: DomainConfig, exc: KeyError) -> MissingIOKeyError:
    """Create a MissingIOKeyError with context from a KeyError."""
    key = exc.args[0] if exc.args else "<unknown>"
    return MissingIOKeyError(
        domain=domain_name,
        key=str(key),
        available_inputs=sorted(domain_cfg.inputs.keys()),
        available_outputs=sorted(domain_cfg.outputs.keys()),
    )


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
        except KeyError as exc:
            raise _missing_io_key_error(domain_name, domain_cfg, exc) from exc
        except Exception as exc:
            msg = "Domain execution failed"
            raise DomainExecutionError(domain=domain_name, message=msg) from exc
        logger.info("Completed domain")


def _execute_domain(domain_name: str, domain_cfg: DomainConfig) -> None:
    """Execute a single domain with error isolation."""
    logger = get_domain_logger("orchestrator", domain_name)

    if not domain_cfg.enabled:
        logger.info("Skipping domain (disabled)")
        return

    logger.info("Starting domain")
    try:
        runner = _load_domain_runner(domain_name)
        runner(domain_cfg)
        logger.info("Completed domain")
    except (DomainNotFoundError, DomainInterfaceError) as exc:
        logger.error(f"Domain setup error: {exc}")
    except KeyError as exc:
        err = _missing_io_key_error(domain_name, domain_cfg, exc)
        logger.error(f"Data handling error: {err}")
    except DataHandlingError as exc:
        logger.error(f"Data handling error: {exc}", exc_info=True)
    except Exception as exc:
        logger.error(f"Unexpected error during domain execution: {exc}", exc_info=True)


def _execute_domain_chunk(domain_items: list[tuple[str, DomainConfig]], thread_workers: int | None) -> None:
    """Execute a chunk of domains. Uses threads if thread_workers > 1."""
    if thread_workers and thread_workers > 1 and len(domain_items) > 1:
        with ThreadPoolExecutor(max_workers=thread_workers, thread_name_prefix="domain") as executor:
            for domain_name, domain_cfg in domain_items:
                executor.submit(_execute_domain, domain_name, domain_cfg)
    else:
        for domain_name, domain_cfg in domain_items:
            _execute_domain(domain_name, domain_cfg)


def _chunk_domains(domain_items: list[tuple[str, DomainConfig]], max_chunks: int | None) -> list[list[tuple[str, DomainConfig]]]:
    """Split domains into chunks for process workers."""
    if not domain_items:
        return []

    if max_chunks is None:
        max_chunks = os.cpu_count() or 1
    max_chunks = max(1, max_chunks)
    chunk_size = max(1, math.ceil(len(domain_items) / max_chunks))
    return [domain_items[i : i + chunk_size] for i in range(0, len(domain_items), chunk_size)]


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
    selected = list(_iter_selected_domains(cfg, allowed_domains))
    p_cfg = cfg.execution.parallel.processes
    t_cfg = cfg.execution.parallel.threads

    # Single entry point for ProcessPool
    if p_cfg.enabled and len(selected) > 1:
        chunks = _chunk_domains(selected, p_cfg.max_workers)
        with ProcessPoolExecutor(max_workers=p_cfg.max_workers) as executor:
            for chunk in chunks:
                executor.submit(_execute_domain_chunk, chunk, t_cfg.max_workers if t_cfg.enabled else None)
    
    # Threading only
    elif t_cfg.enabled and len(selected) > 1:
        with ThreadPoolExecutor(max_workers=t_cfg.max_workers) as executor:
            for domain_name, domain_cfg in selected:
                executor.submit(_execute_domain, domain_name, domain_cfg)

    # Fallback to Serial
    else:
        for domain_name, domain_cfg in selected:
            _execute_domain(domain_name, domain_cfg)
