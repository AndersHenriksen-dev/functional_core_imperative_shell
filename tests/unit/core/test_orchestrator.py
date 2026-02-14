"""Tests for domain orchestration."""

from __future__ import annotations

import types

import pytest

from insert_package_name.core.errors import DomainExecutionError, DomainInterfaceError, DomainNotFoundError
from insert_package_name.core.orchestrator import run_domains
from insert_package_name.schema.types import DomainConfig


def test_run_domains_happy_path(monkeypatch, global_config_factory) -> None:
    calls: list[str] = []

    def runner(_cfg):
        calls.append("ran")

    module = types.SimpleNamespace(run=runner)
    monkeypatch.setattr("insert_package_name.core.orchestrator.importlib.import_module", lambda _: module)

    cfg = global_config_factory({"example_domain": DomainConfig(name="Example Domain")})
    run_domains(cfg)

    assert calls == ["ran"]


def test_run_domains_skips_disabled(monkeypatch, global_config_factory) -> None:
    calls: list[str] = []

    def runner(_cfg):
        calls.append("ran")

    module = types.SimpleNamespace(run=runner)
    monkeypatch.setattr("insert_package_name.core.orchestrator.importlib.import_module", lambda _: module)

    cfg = global_config_factory({"example_domain": DomainConfig(name="Example Domain", enabled=False)})
    run_domains(cfg)

    assert calls == []


def test_run_domains_filters_by_active_domains(monkeypatch, global_config_factory) -> None:
    calls: list[str] = []

    def runner(_cfg):
        calls.append(_cfg.name)

    module = types.SimpleNamespace(run=runner)
    monkeypatch.setattr("insert_package_name.core.orchestrator.importlib.import_module", lambda _: module)

    cfg = global_config_factory(
        {
            "domain_a": DomainConfig(name="Domain A"),
            "domain_b": DomainConfig(name="Domain B"),
        },
        active_domains=["domain_b"],
    )

    run_domains(cfg)

    assert calls == ["Domain B"]


def test_run_domains_filters_by_tags(monkeypatch, global_config_factory) -> None:
    calls: list[str] = []

    def runner(_cfg):
        calls.append(_cfg.name)

    module = types.SimpleNamespace(run=runner)
    monkeypatch.setattr("insert_package_name.core.orchestrator.importlib.import_module", lambda _: module)

    cfg = global_config_factory(
        {
            "domain_a": DomainConfig(name="Domain A", tags=["daily"]),
            "domain_b": DomainConfig(name="Domain B", tags=["monthly"]),
        },
        active_tags=["daily"],
    )

    run_domains(cfg)

    assert calls == ["Domain A"]


def test_domain_module_not_found(monkeypatch, global_config_factory) -> None:
    def _raise(_):
        raise ModuleNotFoundError("missing")

    monkeypatch.setattr("insert_package_name.core.orchestrator.importlib.import_module", _raise)

    cfg = global_config_factory({"missing_domain": DomainConfig(name="Missing")})

    with pytest.raises(DomainNotFoundError):
        run_domains(cfg)


def test_domain_interface_error(monkeypatch, global_config_factory) -> None:
    module = types.SimpleNamespace()
    monkeypatch.setattr("insert_package_name.core.orchestrator.importlib.import_module", lambda _: module)

    cfg = global_config_factory({"bad_domain": DomainConfig(name="Bad")})

    with pytest.raises(DomainInterfaceError):
        run_domains(cfg)


def test_domain_execution_error(monkeypatch, global_config_factory) -> None:
    def runner(_cfg):
        raise ValueError("boom")

    module = types.SimpleNamespace(run=runner)
    monkeypatch.setattr("insert_package_name.core.orchestrator.importlib.import_module", lambda _: module)

    cfg = global_config_factory({"bad_domain": DomainConfig(name="Bad")})

    with pytest.raises(DomainExecutionError):
        run_domains(cfg)
