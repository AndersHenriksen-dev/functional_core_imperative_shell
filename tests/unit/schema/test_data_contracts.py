"""Tests for data contract schemas."""

from __future__ import annotations

import pandas as pd
import pytest
from pandera.errors import SchemaError

from insert_package_name.schema.data_contracts import SilverCustomersSchema, SilverTransactionsSchema


class TestSilverCustomersSchema:
    """Test the SilverCustomersSchema."""

    def test_valid_customers_data(self):
        """Test valid customers data passes validation."""
        data = pd.DataFrame({"customer_id": [1, 2, 3], "age": [25, 30, 35], "country": ["US", "CA", "UK"]})

        # Should not raise an exception
        validated = SilverCustomersSchema.validate(data)
        assert len(validated) == 3
        assert list(validated.columns) == ["customer_id", "age", "country"]

    def test_invalid_customers_data_negative_age(self):
        """Test customers data with negative age fails validation."""
        data = pd.DataFrame(
            {
                "customer_id": [1, 2],
                "age": [-5, 30],  # Negative age should fail
                "country": ["US", "CA"],
            }
        )

        with pytest.raises(SchemaError):
            SilverCustomersSchema.validate(data)

    def test_invalid_customers_data_missing_column(self):
        """Test customers data missing required column fails validation."""
        data = pd.DataFrame(
            {
                "customer_id": [1, 2],
                "age": [25, 30],
                # Missing country column
            }
        )

        with pytest.raises(SchemaError):
            SilverCustomersSchema.validate(data)

    def test_invalid_customers_data_wrong_type(self):
        """Test customers data with wrong column type fails validation."""
        data = pd.DataFrame(
            {
                "customer_id": ["A", "B"],  # Should be int
                "age": [25, 30],
                "country": ["US", "CA"],
            }
        )

        with pytest.raises(SchemaError):
            SilverCustomersSchema.validate(data)

    def test_customers_schema_strict_mode(self):
        """Test that extra columns are rejected in strict mode."""
        data = pd.DataFrame(
            {
                "customer_id": [1, 2],
                "age": [25, 30],
                "country": ["US", "CA"],
                "extra_column": ["value1", "value2"],  # Extra column should fail
            }
        )

        with pytest.raises(SchemaError):
            SilverCustomersSchema.validate(data)

    def test_customers_schema_coercion(self):
        """Test that data types are coerced when coerce=True."""
        data = pd.DataFrame(
            {
                "customer_id": [1.0, 2.0],  # Float should be coerced to int
                "age": [25.0, 30.0],  # Float should be coerced to int
                "country": ["US", "CA"],
            }
        )

        validated = SilverCustomersSchema.validate(data)
        assert validated["customer_id"].dtype == "int64"
        assert validated["age"].dtype == "int64"


class TestSilverTransactionsSchema:
    """Test the SilverTransactionsSchema."""

    def test_valid_transactions_data(self):
        """Test valid transactions data passes validation."""
        data = pd.DataFrame({"customer_id": [1, 2, 1, 3], "amount": [100.50, 250.00, 75.25, 300.00]})

        # Should not raise an exception
        validated = SilverTransactionsSchema.validate(data)
        assert len(validated) == 4
        assert list(validated.columns) == ["customer_id", "amount"]

    def test_invalid_transactions_data_negative_amount(self):
        """Test transactions data with negative amount fails validation."""
        data = pd.DataFrame(
            {
                "customer_id": [1, 2],
                "amount": [-50.00, 100.00],  # Negative amount should fail
            }
        )

        with pytest.raises(SchemaError):
            SilverTransactionsSchema.validate(data)

    def test_invalid_transactions_data_missing_column(self):
        """Test transactions data missing required column fails validation."""
        data = pd.DataFrame(
            {
                "customer_id": [1, 2]
                # Missing amount column
            }
        )

        with pytest.raises(SchemaError):
            SilverTransactionsSchema.validate(data)

    def test_invalid_transactions_data_wrong_type(self):
        """Test transactions data with wrong column type fails validation."""
        data = pd.DataFrame(
            {
                "customer_id": ["A", "B"],  # Should be int
                "amount": [100.50, 250.00],
            }
        )

        with pytest.raises(SchemaError):
            SilverTransactionsSchema.validate(data)

    def test_transactions_schema_strict_mode(self):
        """Test that extra columns are rejected in strict mode."""
        data = pd.DataFrame(
            {
                "customer_id": [1, 2],
                "amount": [100.50, 250.00],
                "extra_column": ["value1", "value2"],  # Extra column should fail
            }
        )

        with pytest.raises(SchemaError):
            SilverTransactionsSchema.validate(data)

    def test_transactions_schema_coercion(self):
        """Test that data types are coerced when coerce=True."""
        data = pd.DataFrame(
            {
                "customer_id": [1.0, 2.0],  # Float should be coerced to int
                "amount": [100, 250],  # Int should be coerced to float
            }
        )

        validated = SilverTransactionsSchema.validate(data)
        assert validated["customer_id"].dtype == "int64"
        assert validated["amount"].dtype == "float64"
