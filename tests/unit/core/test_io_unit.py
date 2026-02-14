"""Tests for IO helpers."""

from __future__ import annotations

import importlib

import pytest

from insert_package_name.core import io
from insert_package_name.core.errors import IOConfigError, OptionalDependencyError, UnsupportedFormatError
from insert_package_name.schema.types import FileFormat, IOConfig


def test_unsupported_format_raises(tmp_path, monkeypatch) -> None:
    path = tmp_path / "data.csv"
    cfg = IOConfig(path=str(path), format=FileFormat.CSV)

    readers = io._READERS.copy()
    monkeypatch.setattr(io, "_READERS", {})

    try:
        with pytest.raises(UnsupportedFormatError):
            io.read_dataframe(cfg)
    finally:
        monkeypatch.setattr(io, "_READERS", readers)


def test_sql_missing_query_or_table_raises() -> None:
    cfg = IOConfig(path="sqlite:///:memory:", format=FileFormat.SQL)

    with pytest.raises(IOConfigError):
        io.read_dataframe(cfg)


def test_delta_missing_dependency_raises() -> None:
    try:
        importlib.import_module("deltalake")
        pytest.skip("deltalake installed; optional dependency test not applicable")
    except ModuleNotFoundError:
        cfg = IOConfig(path="/tmp/delta", format=FileFormat.DELTA)
        with pytest.raises(OptionalDependencyError):
            io.read_dataframe(cfg)
