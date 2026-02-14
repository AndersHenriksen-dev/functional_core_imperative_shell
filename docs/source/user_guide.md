# User Guide

This guide explains how to run pipelines, how the architecture fits together, and how to extend the system safely.

## Design overview

The system is built around a few simple, composable concepts:

- **Contracts**: Pandera schemas define what inputs and outputs must look like.
- **Domain modules**: Each domain owns business logic and exposes a `run` function.
- **IO**: `read_dataframe` and `write_dataframe` handle registry-based IO.
- **Orchestration**: `run_domains` executes selected domains based on config.
- **Configuration**: Pydantic models validate Hydra configs into dataclasses.

This structure keeps pipelines readable and encourages SOLID principles:

- **Single Responsibility**: Domain modules own business logic; IO handles persistence.
- **Open/Closed**: New domains are added without editing core logic.
- **Dependency Injection**: IO and configuration can be overridden for tests.

The example domain reads silver inputs and produces gold outputs under [data/gold](../../data/gold).

## Configuration model

### Architecture

The system uses a **safe-loading pattern** where domains are loaded iteratively with error isolation. If one domain config is broken, it's logged and skipped—other domains continue executing.

Hydra composes configuration from [configs](../../configs):

- [configs/config.yaml](../../configs/config.yaml) sets defaults and active filters.
- [configs/domains](../../configs/domains) defines per-domain inputs, outputs, and params.
- [configs/inputs](../../configs/inputs) defines shared input configurations (DRY).
- [configs/schedule](../../configs/schedule) defines reusable schedule presets.
- [configs/batch](../../configs/batch) defines batch run configurations.
- [configs/infrastructure](../../configs/infrastructure) defines logging.

### Shared Inputs (DRY Principle)

Inputs are defined once and referenced by name:

```yaml
# configs/inputs/common.yaml
customers:
  path: ${base_input_path}/customers.csv
  format: csv
transactions:
  path: ${base_input_path}/transactions.csv
  format: csv
```

Domains reference inputs by name:

```yaml
# configs/domains/example_domain.yaml
defaults:
  - /schedule@example_domain.schedule: disabled
  - _self_

example_domain:
  name: "Example Domain"
  enabled: true
  tags: ["daily"]
  inputs: [customers, transactions]  # Reference by name
  params:
    score_threshold: 0.7
  outputs:
    scores:
      path: ${base_output_path}/example_domain/scores.csv
      format: csv
    metrics:
      path: ${base_output_path}/example_domain/metrics.csv
      format: csv
```

### Schedule Presets

Schedule configurations are composable:

```yaml
# configs/schedule/daily.yaml
enabled: true
interval: "daily"
hour: 2
minute: 0
```

Reference in domain defaults:

```yaml
defaults:
  - /schedule@example_domain.schedule: daily  # Uses daily preset
```

### Batch Configurations

Define which domains to run:

```yaml
# configs/batch/daily.yaml
domains_to_run:
  - example_domain
active_tags: ["daily"]
```

Run batches via CLI:

```bash
python -m insert_package_name.main batch=daily
```

## IO and format options

The IO layer supports CSV, Parquet, JSON, Excel, Feather, ORC, Pickle, SQL, and Delta. Refer to the IO
formats guide for supported options and examples:

- [IO formats reference](io_formats.md)

## Running the pipelines

Run all configured domains:

```bash
python -m insert_package_name.main
```

### Run specific domains

The most common use case is running a specific subset of domains:

```bash
# Run just sales and finance domains
python -m insert_package_name.main active_domains=[sales,finance]

# Run a single domain
python -m insert_package_name.main active_domains=[example_domain]

# Run all domains with a specific tag
python -m insert_package_name.main active_tags=[daily]

# Run multiple domains with specific tags
python -m insert_package_name.main active_tags=[critical,daily]
```

### Override configuration

Override values at runtime using Hydra syntax:

```bash
# Override shared inputs
python -m insert_package_name.main inputs.customers.path="sales/customers.csv"

# Override domain outputs
python -m insert_package_name.main domains.example_domain.outputs.scores.path="sales/custom_scores.csv"

# Combine domain selection with overrides
python -m insert_package_name.main active_domains=[sales,finance] base_input_path=/data/custom_silver
```

## Docker

Build and run with Docker Compose:

```bash
docker compose up app
```

Run the scheduler instead:

```bash
docker compose up scheduler
```

Copy [./.env.example](../../.env.example) to [.env](../../.env) to provide environment variables used by overrides.

## Secrets management

Use environment variables for secrets and reference them in config files with Hydra interpolation:

```yaml
# configs/domains/example_domain.yaml
example_domain:
  inputs:
    customers:
      path: ${oc.env:CUSTOMERS_PATH}
      format: csv
```

## Validation adapters

Validation happens inside domain logic with Pandera schemas. If you want to swap validation behavior, replace the Pandera decorators or add domain-level guards.

## Adding a new domain

Create a new domain module and wire it into configuration:

1. Add a module under [src/insert_package_name/domains/example_domain/pipeline.py](../../src/insert_package_name/domains/example_domain/pipeline.py).
2. Implement a `run(cfg: DomainConfig)` function.
3. Define Pandera schemas under [src/insert_package_name/domains/example_domain/schemas.py](../../src/insert_package_name/domains/example_domain/schemas.py).
4. Add a domain config file under [configs/domains](../../configs/domains).
5. Update [configs/config.yaml](../../configs/config.yaml) defaults to include the new domain.

Minimal example for a new domain named `marketing`:

```python
from __future__ import annotations

from insert_package_name.core import read_dataframe, write_dataframe
from insert_package_name.core.logging import get_domain_logger
from insert_package_name.schema.types import DomainConfig


def run(cfg: DomainConfig) -> None:
    logger = get_domain_logger(__name__, cfg.name)

    sales = read_dataframe(cfg.inputs["sales"])
    summary = sales.groupby("region", as_index=False)["revenue"].sum()

    write_dataframe(summary, cfg.outputs["summary"])
    logger.info("Wrote %s rows", len(summary))
```

Config additions:

```yaml
# configs/domains/marketing.yaml
marketing:
  name: "Marketing"
  enabled: true
  tags: ["weekly"]
  inputs:
    sales:
      path: ${hydra:runtime.cwd}/data/silver/sales.csv
      format: csv
  outputs:
    summary:
      path: ${hydra:runtime.cwd}/data/gold/marketing/summary.csv
      format: csv
```

## How domains load

Domains are loaded dynamically from `insert_package_name.domains.<name>.pipeline`, and the `run` entry point is invoked. If a domain module is missing or does not export `run`, the orchestrator raises a domain error.

## Testing strategy

Tests mirror the package structure and validate both behavior and contracts:

- Unit tests for core utilities, errors, and IO behavior.
- Integration tests for domain pipelines.
- End-to-end tests that run `python -m insert_package_name.main` with real IO.

Run all tests:

```bash
python -m pytest -q
```

## Debugging tips

- Logs are written to `logs/` when file logging is enabled.
- Use `--cfg job` to inspect the full Hydra config.
- Keep pipeline logic small so failures are easy to isolate.

## Extension points

- Provide alternative readers/writers for custom storage backends.
- Swap config files with Hydra overrides for new environments.
- Add new domains by exporting a `run` function.
