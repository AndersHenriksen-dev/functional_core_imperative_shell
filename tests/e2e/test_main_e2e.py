"""End-to-end test for the main orchestrator."""

from __future__ import annotations

import csv
import subprocess
import sys
from pathlib import Path


def _write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def test_main_runs_with_overrides(tmp_path: Path) -> None:
    """Run the main entry point with filesystem overrides."""
    customers_path = tmp_path / "silver" / "customers.csv"
    transactions_path = tmp_path / "silver" / "transactions.csv"
    scores_path = tmp_path / "gold" / "scores.csv"
    metrics_path = tmp_path / "gold" / "metrics.csv"

    _write_csv(
        customers_path,
        [
            {"customer_id": 1, "age": 30, "country": "US"},
            {"customer_id": 2, "age": 50, "country": "DK"},
        ],
    )
    _write_csv(
        transactions_path,
        [
            {"customer_id": 1, "amount": 120.0},
            {"customer_id": 2, "amount": 0.0},
        ],
    )

    args = [
        sys.executable,
        "-m",
        "insert_package_name.main",
        "active_domains=[example_domain]",
        f"inputs.customers.path={customers_path.as_posix()}",
        f"inputs.transactions.path={transactions_path.as_posix()}",
        f"domains.example_domain.outputs.scores.path={scores_path.as_posix()}",
        f"domains.example_domain.outputs.metrics.path={metrics_path.as_posix()}",
        "logging.to_console=false",
        "logging.to_file=false",
    ]

    result = subprocess.run(args, cwd=tmp_path, capture_output=True, text=True, check=True)

    assert result.returncode == 0
    assert scores_path.exists()
    assert metrics_path.exists()
