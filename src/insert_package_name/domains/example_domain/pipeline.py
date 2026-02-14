"""Pipeline composition for the example domain."""

from __future__ import annotations

from insert_package_name.core import read_dataframe, write_dataframe
from insert_package_name.core.logging import get_domain_logger
from insert_package_name.domains.example_domain.ops import compute_metrics, compute_scores
from insert_package_name.schema.types import DomainConfig


def run(cfg: DomainConfig) -> None:
    """Run the example domain pipeline.

    Parameters
    ----------
    cfg : DomainConfig
        Domain configuration with inputs, outputs, and params.

    """
    logger = get_domain_logger(__name__, cfg.name)

    customers = read_dataframe(cfg.inputs["customers"])
    transactions = read_dataframe(cfg.inputs["transactions"])

    threshold = float(cfg.params.get("score_threshold", 0.7))
    scores = compute_scores(customers, transactions, threshold)
    metrics = compute_metrics(scores)

    write_dataframe(scores, cfg.outputs["scores"])
    write_dataframe(metrics, cfg.outputs["metrics"])

    logger.info("Wrote %s scores and %s metrics", len(scores), len(metrics))
