"""Tests for example domain ops."""

from __future__ import annotations

from insert_package_name.domains.example_domain.ops import compute_metrics, compute_scores


def test_compute_scores_and_metrics(customers_df, transactions_df) -> None:
    scores = compute_scores(customers_df, transactions_df, threshold=0.5)
    assert set(scores.columns) == {"customer_id", "churn_probability", "is_high_risk"}
    assert len(scores) == 2

    metrics = compute_metrics(scores)
    assert set(metrics.columns) == {"metric", "value"}
    assert len(metrics) == 2
