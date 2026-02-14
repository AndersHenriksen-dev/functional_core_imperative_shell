"""Pandera schemas for shared silver data contracts."""

from __future__ import annotations

import pandera.pandas as pa
from pandera.typing import Series


class SilverCustomersSchema(pa.DataFrameModel):
    """Schema for silver-level customers data."""

    customer_id: Series[int]
    age: Series[int] = pa.Field(ge=0)
    country: Series[str]

    class Config:
        """Pandera configuration for strict schema enforcement."""

        strict = True
        coerce = True


class SilverTransactionsSchema(pa.DataFrameModel):
    """Schema for silver-level transactions data."""

    customer_id: Series[int]
    amount: Series[float] = pa.Field(ge=0)

    class Config:
        """Pandera configuration for strict schema enforcement."""

        strict = True
        coerce = True
