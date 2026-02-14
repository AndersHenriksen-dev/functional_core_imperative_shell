"""Pure transformation logic for the example domain."""

from __future__ import annotations

import pandas as pd
import pandera.pandas as pa
from pandera.typing import DataFrame

from insert_package_name.domains.example_domain.schemas import GoldMetricsSchema, GoldScoresSchema
from insert_package_name.schema.data_contracts import SilverCustomersSchema, SilverTransactionsSchema


@pa.check_types
def compute_scores(
    customers: DataFrame[SilverCustomersSchema],
    transactions: DataFrame[SilverTransactionsSchema],
    threshold: float,
) -> DataFrame[GoldScoresSchema]:
    """Compute churn risk scores for each customer.

    Parameters
    ----------
    customers : DataFrame[SilverCustomersSchema]
        Customer records with identifiers and demographics.
    transactions : DataFrame[SilverTransactionsSchema]
        Transaction records with amounts.
    threshold : float
        Churn probability threshold for high-risk classification.

    Returns
    -------
    DataFrame[GoldScoresSchema]
        Scores with churn probability and high-risk flags.

    """
    totals = transactions.groupby("customer_id", as_index=False)["amount"].sum()
    merged = customers.merge(totals, on="customer_id", how="left").fillna({"amount": 0})

    max_amount = merged["amount"].max() or 1.0
    merged["churn_probability"] = (1.0 - (merged["amount"] / max_amount)).clip(0, 1)
    merged["is_high_risk"] = merged["churn_probability"] > threshold

    return merged[["customer_id", "churn_probability", "is_high_risk"]]


@pa.check_types
def compute_metrics(scores: DataFrame[GoldScoresSchema]) -> DataFrame[GoldMetricsSchema]:
    """Summarize score counts into metrics.

    Parameters
    ----------
    scores : DataFrame[GoldScoresSchema]
        Scored customers with high-risk flags.

    Returns
    -------
    DataFrame[GoldMetricsSchema]
        Metrics dataframe with counts.

    """
    summary = pd.DataFrame(
        {
            "metric": ["customers", "high_risk"],
            "value": [len(scores), scores["is_high_risk"].sum()],
        }
    )
    return summary
