"""Domain creation utilities."""

from __future__ import annotations

from pathlib import Path

import click

from insert_package_name.main import get_config_directory


def create_domain_template(domain_name: str, target_dir: Path) -> None:
    """Create a domain template with all necessary files."""
    domain_dir = target_dir / "domains" / domain_name
    domain_dir.mkdir(parents=True, exist_ok=True)

    # Create __init__.py
    (domain_dir / "__init__.py").write_text('"""Domain initialization."""\n')

    # Create ops.py
    ops_content = f'''"""Business logic operations for {domain_name} domain."""

from __future__ import annotations

import pandas as pd
from pandera.typing import DataFrame

from insert_package_name.schema.types import GoldMetricsSchema, GoldScoresSchema


def compute_scores(
    customers: DataFrame,
    transactions: DataFrame,
    threshold: float = 0.7
) -> DataFrame[GoldScoresSchema]:
    """Compute scores for customers based on transaction data.

    Parameters
    ----------
    customers : DataFrame
        Customer data.
    transactions : DataFrame
        Transaction data.
    threshold : float
        Risk threshold for classification.

    Returns
    -------
    DataFrame[GoldScoresSchema]
        Scored customer data.
    """
    # TODO: Implement your scoring logic here
    # This is just an example implementation
    totals = transactions.groupby("customer_id", as_index=False)["amount"].sum()
    merged = customers.merge(totals, on="customer_id", how="left").fillna({{"amount": 0}})

    max_amount = merged["amount"].max() or 1.0
    merged["churn_probability"] = (1.0 - (merged["amount"] / max_amount)).clip(0, 1)
    merged["is_high_risk"] = merged["churn_probability"] > threshold

    return merged[["customer_id", "churn_probability", "is_high_risk"]]


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
    # TODO: Implement your metrics logic here
    summary = pd.DataFrame({{
        "metric": ["customers", "high_risk"],
        "value": [len(scores), scores["is_high_risk"].sum()],
    }})
    return summary
'''
    (domain_dir / "ops.py").write_text(ops_content)

    # Create pipeline.py
    pipeline_content = f'''"""Pipeline composition for the {domain_name} domain."""

from __future__ import annotations

from insert_package_name.core import read_dataframe, write_dataframe
from insert_package_name.core.logging import get_domain_logger
from insert_package_name.domains.{domain_name}.ops import compute_metrics, compute_scores
from insert_package_name.schema.types import DomainConfig


def run(cfg: DomainConfig) -> None:
    """Run the {domain_name} domain pipeline.

    Parameters
    ----------
    cfg : DomainConfig
        Domain configuration with inputs, outputs, and params.
    """
    logger = get_domain_logger(__name__, cfg.name)

    # TODO: Update input names based on your data sources
    customers = read_dataframe(cfg.inputs["customers"])
    transactions = read_dataframe(cfg.inputs["transactions"])

    threshold = float(cfg.params.get("score_threshold", 0.7))
    scores = compute_scores(customers, transactions, threshold)
    metrics = compute_metrics(scores)

    # TODO: Update output names based on your requirements
    write_dataframe(scores, cfg.outputs["scores"])
    write_dataframe(metrics, cfg.outputs["metrics"])

    logger.info("Wrote %s scores and %s metrics", len(scores), len(metrics))
'''
    (domain_dir / "pipeline.py").write_text(pipeline_content)

    # Create schemas.py
    schemas_content = '''"""Data schemas for the domain."""

from __future__ import annotations

import pandera as pa
from pandera import Column, DataFrameSchema


# TODO: Define your input schemas
class CustomerSchema(DataFrameSchema):
    """Schema for customer data."""
    customer_id: pa.typing.Index[int] = pa.Field(unique=True)
    # Add your customer columns here
    # name: pa.typing.Series[str] = pa.Field()
    # email: pa.typing.Series[str] = pa.Field()


class TransactionSchema(DataFrameSchema):
    """Schema for transaction data."""
    customer_id: pa.typing.Series[int] = pa.Field()
    amount: pa.typing.Series[float] = pa.Field()
    # Add your transaction columns here
    # date: pa.typing.Series[str] = pa.Field()
    # category: pa.typing.Series[str] = pa.Field()


# TODO: Define your output schemas
class GoldScoresSchema(DataFrameSchema):
    """Schema for scored customer data."""
    customer_id: pa.typing.Series[int] = pa.Field()
    churn_probability: pa.typing.Series[float] = pa.Field(ge=0, le=1)
    is_high_risk: pa.typing.Series[bool] = pa.Field()


class GoldMetricsSchema(DataFrameSchema):
    """Schema for metrics data."""
    metric: pa.typing.Series[str] = pa.Field()
    value: pa.typing.Series[float] = pa.Field()
'''
    (domain_dir / "schemas.py").write_text(schemas_content)


def create_domain_config(domain_name: str, config_dir: Path) -> None:
    """Create domain configuration files."""
    domains_dir = config_dir / "domains"
    domains_dir.mkdir(parents=True, exist_ok=True)

    # Create domain YAML config
    config_content = f"""defaults:
  - /schedule@example_{domain_name}.schedule: disabled  # Could be set to daily
  - _self_

{domain_name}:
  name: "{domain_name.replace("_", " ").title()}"
  enabled: true
  tags: ["daily"]  # TODO: Update tags as needed
  inputs:
    customers:  # TODO: Update input names and paths
      path: ${{base_input_path}}/customers.csv
      format: csv
    transactions:  # TODO: Update input names and paths
      path: ${{base_input_path}}/transactions.csv
      format: csv
  params:
    score_threshold: 0.7  # TODO: Update parameters as needed
  outputs:
    scores:
      path: ${{base_output_path}}/{domain_name}/scores.csv
      format: csv
    metrics:
      path: ${{base_output_path}}/{domain_name}/metrics.csv
      format: csv
"""
    (domains_dir / f"{domain_name}.yaml").write_text(config_content)

    # Update main config to include the new domain
    main_config_path = config_dir / "config.yaml"
    if main_config_path.exists():
        content = main_config_path.read_text()
        # Add the domain to defaults if not already there
        if f"- {domain_name}" not in content:
            # Find the domains section and add the new domain
            lines = content.split("\n")
            for i, line in enumerate(lines):
                if line.strip().startswith("domains:"):
                    # Insert after the domains: line
                    lines.insert(i + 1, f"      - {domain_name}")
                    break
            main_config_path.write_text("\n".join(lines))


def create_domain_impl(domain_name: str, target_dir: str, config_dir: str | None) -> None:
    """Create a new domain with template files."""
    target_path = Path(target_dir)
    config_path = Path(config_dir) if config_dir else Path(get_config_directory())

    # Validate domain name
    if not domain_name.replace("_", "").isalnum():
        raise ValueError("Domain name must contain only letters, numbers, and underscores")

    print(f"Creating domain '{domain_name}'...")

    # Create domain code
    create_domain_template(domain_name, target_path)
    print(f"[OK] Created domain code in {target_path}/domains/{domain_name}/")

    # Create domain config
    create_domain_config(domain_name, config_path)
    print(f"[OK] Created domain config in {config_path}/domains/{domain_name}.yaml")

    print("\nNext steps:")
    print(f"1. Edit {target_path}/domains/{domain_name}/schemas.py to define your data schemas")
    print(f"2. Update {target_path}/domains/{domain_name}/ops.py with your business logic")
    print(f"3. Modify {target_path}/domains/{domain_name}/pipeline.py to orchestrate your operations")
    print(f"4. Update {config_path}/domains/{domain_name}.yaml with correct input/output paths")
    print("5. Run 'python -m insert_package_name.main' to test your domain")


@click.command()
@click.argument("domain_name")
@click.option("--target-dir", default=".", help="Target directory for the domain")
@click.option("--config-dir", default=None, help="Config directory to update")
def create_domain(domain_name: str, target_dir: str, config_dir: str | None) -> None:
    """Create a new domain with template files."""
    create_domain_impl(domain_name, target_dir, config_dir)
