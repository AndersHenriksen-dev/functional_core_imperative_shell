"""Gold schemas for the example domain."""

from __future__ import annotations

import pandera.pandas as pa
from pandera.typing import Series


class GoldScoresSchema(pa.DataFrameModel):
    """Schema for gold-level churn scores."""

    customer_id: Series[int]
    churn_probability: Series[float] = pa.Field(ge=0, le=1)
    is_high_risk: Series[bool]

    class Config:
        """Pandera configuration for strict schema enforcement."""

        strict = True
        coerce = True


class GoldMetricsSchema(pa.DataFrameModel):
    """Schema for gold-level metrics."""

    metric: Series[str]
    value: Series[float]

    class Config:
        """Pandera configuration for strict schema enforcement."""

        strict = True
        coerce = True
