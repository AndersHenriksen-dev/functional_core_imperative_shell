"""Integration tests for IO helpers."""

from __future__ import annotations

from insert_package_name.core import io
from insert_package_name.schema.types import FileFormat, IOConfig


def test_read_write_csv_roundtrip(tmp_path, simple_df) -> None:
    """Verify CSV write and read produce identical data."""
    path = tmp_path / "data.csv"
    cfg = IOConfig(path=str(path), format=FileFormat.CSV)

    io.write_dataframe(simple_df, cfg)
    loaded = io.read_dataframe(cfg)

    simple_df.reset_index(drop=True, inplace=True)
    loaded.reset_index(drop=True, inplace=True)
    assert loaded.equals(simple_df)
