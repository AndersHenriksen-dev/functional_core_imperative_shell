"""Dataframe IO with registry-based extensibility."""

from __future__ import annotations

import os
import posixpath
from collections.abc import Callable
from typing import Any

import fsspec
import pandas as pd
from fsspec.core import url_to_fs

from insert_package_name.core.errors import (
    DataHandlingError,
    IOConfigError,
    IOReadError,
    IOWriteError,
    OptionalDependencyError,
    UnsupportedFormatError,
)
from insert_package_name.schema.types import FileFormat, IOConfig

Reader = Callable[[IOConfig], pd.DataFrame]
Writer = Callable[[pd.DataFrame, IOConfig], None]

_READERS: dict[FileFormat, Reader] = {}
_WRITERS: dict[FileFormat, Writer] = {}


def register_reader(file_format: FileFormat, reader: Reader) -> None:
    """Register a reader for a file format.

    Parameters
    ----------
    file_format : FileFormat
        File format to associate with the reader.
    reader : Reader
        Callable that reads an IOConfig into a dataframe.

    """
    _READERS[file_format] = reader


def register_writer(file_format: FileFormat, writer: Writer) -> None:
    """Register a writer for a file format.

    Parameters
    ----------
    file_format : FileFormat
        File format to associate with the writer.
    writer : Writer
        Callable that writes a dataframe using an IOConfig.

    """
    _WRITERS[file_format] = writer


def _ensure_parent_dir(path: str, storage_options: dict[str, Any]) -> None:
    """Ensure the parent directory exists for a target path.

    Parameters
    ----------
    path : str
        Target path or URI.
    storage_options : dict[str, Any]
        fsspec storage options for remote filesystems.

    """
    fs, fs_path = url_to_fs(path, **storage_options)

    parent = os.path.dirname(fs_path) if fs.protocol in {"file", "local"} else posixpath.dirname(fs_path)

    if parent:
        fs.makedirs(parent, exist_ok=True)


def _read_csv(cfg: IOConfig) -> pd.DataFrame:
    """Read a CSV file into a dataframe.

    Parameters
    ----------
    cfg : IOConfig
        IO configuration for the CSV input.

    Returns
    -------
    pandas.DataFrame
        Loaded dataframe.

    """
    return pd.read_csv(cfg.path, storage_options=cfg.storage_options, **cfg.options)


def _write_csv(df: pd.DataFrame, cfg: IOConfig) -> None:
    """Write a dataframe to CSV.

    Parameters
    ----------
    df : pandas.DataFrame
        Dataframe to write.
    cfg : IOConfig
        IO configuration for the CSV output.

    """
    _ensure_parent_dir(cfg.path, cfg.storage_options)
    df.to_csv(cfg.path, index=False, storage_options=cfg.storage_options, **cfg.options)


def _read_parquet(cfg: IOConfig) -> pd.DataFrame:
    """Read a Parquet file into a dataframe.

    Parameters
    ----------
    cfg : IOConfig
        IO configuration for the Parquet input.

    Returns
    -------
    pandas.DataFrame
        Loaded dataframe.

    """
    return pd.read_parquet(cfg.path, storage_options=cfg.storage_options, **cfg.options)


def _write_parquet(df: pd.DataFrame, cfg: IOConfig) -> None:
    """Write a dataframe to Parquet.

    Parameters
    ----------
    df : pandas.DataFrame
        Dataframe to write.
    cfg : IOConfig
        IO configuration for the Parquet output.

    """
    _ensure_parent_dir(cfg.path, cfg.storage_options)
    df.to_parquet(cfg.path, storage_options=cfg.storage_options, **cfg.options)


def _read_json(cfg: IOConfig) -> pd.DataFrame:
    """Read a JSON file into a dataframe.

    Parameters
    ----------
    cfg : IOConfig
        IO configuration for the JSON input.

    Returns
    -------
    pandas.DataFrame
        Loaded dataframe.

    """
    with fsspec.open(cfg.path, "rb", **cfg.storage_options) as handle:
        return pd.read_json(handle, **cfg.options)


def _write_json(df: pd.DataFrame, cfg: IOConfig) -> None:
    """Write a dataframe to JSON.

    Parameters
    ----------
    df : pandas.DataFrame
        Dataframe to write.
    cfg : IOConfig
        IO configuration for the JSON output.

    """
    _ensure_parent_dir(cfg.path, cfg.storage_options)
    with fsspec.open(cfg.path, "w", encoding="utf-8", **cfg.storage_options) as handle:
        df.to_json(handle, **cfg.options)


def _read_excel(cfg: IOConfig) -> pd.DataFrame:
    """Read an Excel file into a dataframe.

    Parameters
    ----------
    cfg : IOConfig
        IO configuration for the Excel input.

    Returns
    -------
    pandas.DataFrame
        Loaded dataframe.

    """
    with fsspec.open(cfg.path, "rb", **cfg.storage_options) as handle:
        return pd.read_excel(handle, **cfg.options)


def _write_excel(df: pd.DataFrame, cfg: IOConfig) -> None:
    """Write a dataframe to Excel.

    Parameters
    ----------
    df : pandas.DataFrame
        Dataframe to write.
    cfg : IOConfig
        IO configuration for the Excel output.

    """
    _ensure_parent_dir(cfg.path, cfg.storage_options)
    with fsspec.open(cfg.path, "wb", **cfg.storage_options) as handle:
        df.to_excel(handle, index=False, **cfg.options)


def _read_feather(cfg: IOConfig) -> pd.DataFrame:
    """Read a Feather file into a dataframe.

    Parameters
    ----------
    cfg : IOConfig
        IO configuration for the Feather input.

    Returns
    -------
    pandas.DataFrame
        Loaded dataframe.

    """
    return pd.read_feather(cfg.path, storage_options=cfg.storage_options, **cfg.options)


def _write_feather(df: pd.DataFrame, cfg: IOConfig) -> None:
    """Write a dataframe to Feather.

    Parameters
    ----------
    df : pandas.DataFrame
        Dataframe to write.
    cfg : IOConfig
        IO configuration for the Feather output.

    """
    _ensure_parent_dir(cfg.path, cfg.storage_options)
    df.to_feather(cfg.path, **cfg.options)


def _read_orc(cfg: IOConfig) -> pd.DataFrame:
    """Read an ORC file into a dataframe.

    Parameters
    ----------
    cfg : IOConfig
        IO configuration for the ORC input.

    Returns
    -------
    pandas.DataFrame
        Loaded dataframe.

    """
    return pd.read_orc(cfg.path, storage_options=cfg.storage_options, **cfg.options)


def _write_orc(df: pd.DataFrame, cfg: IOConfig) -> None:
    """Write a dataframe to ORC.

    Parameters
    ----------
    df : pandas.DataFrame
        Dataframe to write.
    cfg : IOConfig
        IO configuration for the ORC output.

    """
    _ensure_parent_dir(cfg.path, cfg.storage_options)
    df.to_orc(cfg.path, **cfg.options)


def _read_pickle(cfg: IOConfig) -> pd.DataFrame:
    """Read a pickle file into a dataframe.

    Parameters
    ----------
    cfg : IOConfig
        IO configuration for the pickle input.

    Returns
    -------
    pandas.DataFrame
        Loaded dataframe.

    """
    return pd.read_pickle(cfg.path, storage_options=cfg.storage_options, **cfg.options)  # noqa: S301


def _write_pickle(df: pd.DataFrame, cfg: IOConfig) -> None:
    """Write a dataframe to pickle.

    Parameters
    ----------
    df : pandas.DataFrame
        Dataframe to write.
    cfg : IOConfig
        IO configuration for the pickle output.

    """
    _ensure_parent_dir(cfg.path, cfg.storage_options)
    df.to_pickle(cfg.path, **cfg.options)


def _read_sql(cfg: IOConfig) -> pd.DataFrame:
    """Read a table or query from SQL into a dataframe.

    Parameters
    ----------
    cfg : IOConfig
        IO configuration for the SQL input.

    Returns
    -------
    pandas.DataFrame
        Loaded dataframe.

    Raises
    ------
    IOConfigError
        If neither a query nor a table name is provided.

    """
    from sqlalchemy import create_engine

    query = cfg.options.get("query")
    table = cfg.options.get("table")

    if not query and not table:
        msg = "SQL IO requires options.query or options.table"
        raise IOConfigError(message=msg, path=cfg.path, file_format=cfg.format.value)

    engine = create_engine(cfg.path)
    if query:
        return pd.read_sql_query(query, engine, **cfg.options.get("read_options", {}))
    return pd.read_sql_table(table, engine, **cfg.options.get("read_options", {}))


def _write_sql(df: pd.DataFrame, cfg: IOConfig) -> None:
    """Write a dataframe to a SQL table.

    Parameters
    ----------
    df : pandas.DataFrame
        Dataframe to write.
    cfg : IOConfig
        IO configuration for the SQL output.

    Raises
    ------
    IOConfigError
        If a table name is not provided.

    """
    from sqlalchemy import create_engine

    table = cfg.options.get("table")
    if not table:
        msg = "SQL IO requires options.table"
        raise IOConfigError(message=msg, path=cfg.path, file_format=cfg.format.value)

    if_exists = cfg.options.get("if_exists", "replace")
    index = cfg.options.get("index", False)

    engine = create_engine(cfg.path)
    df.to_sql(table, engine, if_exists=if_exists, index=index, **cfg.options.get("write_options", {}))


def _read_delta(cfg: IOConfig) -> pd.DataFrame:
    """Read a Delta table into a dataframe.

    Parameters
    ----------
    cfg : IOConfig
        IO configuration for the Delta input.

    Returns
    -------
    pandas.DataFrame
        Loaded dataframe.

    Raises
    ------
    OptionalDependencyError
        If the deltalake dependency is not installed.

    """
    try:
        from deltalake import DeltaTable
    except ImportError as exc:
        raise OptionalDependencyError(dependency="deltalake", feature="Delta IO") from exc

    table = DeltaTable(cfg.path, storage_options=cfg.storage_options)
    return table.to_pandas()


def _write_delta(df: pd.DataFrame, cfg: IOConfig) -> None:
    """Write a dataframe to a Delta table.

    Parameters
    ----------
    df : pandas.DataFrame
        Dataframe to write.
    cfg : IOConfig
        IO configuration for the Delta output.

    Raises
    ------
    OptionalDependencyError
        If the deltalake dependency is not installed.

    """
    try:
        from deltalake.writer import write_deltalake
    except ImportError as exc:
        raise OptionalDependencyError(dependency="deltalake", feature="Delta IO") from exc

    write_deltalake(cfg.path, df, storage_options=cfg.storage_options, **cfg.options)


register_reader(FileFormat.CSV, _read_csv)
register_writer(FileFormat.CSV, _write_csv)
register_reader(FileFormat.PARQUET, _read_parquet)
register_writer(FileFormat.PARQUET, _write_parquet)
register_reader(FileFormat.JSON, _read_json)
register_writer(FileFormat.JSON, _write_json)
register_reader(FileFormat.EXCEL, _read_excel)
register_writer(FileFormat.EXCEL, _write_excel)
register_reader(FileFormat.FEATHER, _read_feather)
register_writer(FileFormat.FEATHER, _write_feather)
register_reader(FileFormat.ORC, _read_orc)
register_writer(FileFormat.ORC, _write_orc)
register_reader(FileFormat.PICKLE, _read_pickle)
register_writer(FileFormat.PICKLE, _write_pickle)
register_reader(FileFormat.SQL, _read_sql)
register_writer(FileFormat.SQL, _write_sql)
register_reader(FileFormat.DELTA, _read_delta)
register_writer(FileFormat.DELTA, _write_delta)


def read_dataframe(cfg: IOConfig) -> pd.DataFrame:
    """Read a dataframe using the configured reader.

    Parameters
    ----------
    cfg : IOConfig
        IO configuration for the input.

    Returns
    -------
    pandas.DataFrame
        Loaded dataframe.

    Raises
    ------
    UnsupportedFormatError
        If no reader is registered for the format.
    IOReadError
        If the reader fails.
    DataHandlingError
        If a known data handling error is raised.

    """
    reader = _READERS.get(cfg.format)
    if not reader:
        msg = "No reader registered for format"
        raise UnsupportedFormatError(message=msg, path=cfg.path, file_format=cfg.format.value)
    try:
        return reader(cfg)
    except DataHandlingError:
        raise
    except Exception as exc:
        msg = "Failed to read dataset"
        raise IOReadError(message=msg, path=cfg.path, file_format=cfg.format.value) from exc


def write_dataframe(df: pd.DataFrame, cfg: IOConfig) -> None:
    """Write a dataframe using the configured writer.

    Parameters
    ----------
    df : pandas.DataFrame
        Dataframe to write.
    cfg : IOConfig
        IO configuration for the output.

    Raises
    ------
    UnsupportedFormatError
        If no writer is registered for the format.
    IOWriteError
        If the writer fails.
    DataHandlingError
        If a known data handling error is raised.

    """
    writer = _WRITERS.get(cfg.format)
    if not writer:
        msg = "No writer registered for format"
        raise UnsupportedFormatError(message=msg, path=cfg.path, file_format=cfg.format.value)
    try:
        writer(df, cfg)
    except DataHandlingError:
        raise
    except Exception as exc:
        msg = "Failed to write dataset"
        raise IOWriteError(message=msg, path=cfg.path, file_format=cfg.format.value) from exc
