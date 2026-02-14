"""Tests for example domain pipeline composition."""

from __future__ import annotations

from insert_package_name.domains.example_domain import pipeline


def test_pipeline_reads_and_writes(monkeypatch, customers_df, transactions_df, example_domain_config) -> None:
    reads = [customers_df.head(1), transactions_df.head(1)]
    writes = []

    def fake_read(_cfg):
        return reads.pop(0)

    def fake_write(df, _cfg):
        writes.append(df)

    monkeypatch.setattr(pipeline, "read_dataframe", fake_read)
    monkeypatch.setattr(pipeline, "write_dataframe", fake_write)

    pipeline.run(example_domain_config)

    assert len(writes) == 2
