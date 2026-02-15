# insert_package_name

Data handling for domain-oriented pipelines with a single IO surface and explicit schemas.

## Overview

This package standardizes how data is read, validated, and written across domains. Configuration is driven by Hydra with a **safe-loading pattern** that isolates errors, validated with Pydantic, while Pandera schemas keep inputs and outputs explicit.

## Features

- **Registry-based IO**: Support for CSV, Parquet, JSON, Excel, Feather, ORC, Pickle, SQL, and Delta formats
- **Safe-loading Hydra configs**: Broken domain configs don't crash the entire batch
- **Composable configuration**: Shared inputs and schedule presets (DRY principle)
- **Domain pipelines**: Clean separation between orchestration and business logic
- **Pydantic validation**: Clear error messages for configuration issues
- **Automatic domain scheduling**: Run pipelines daily, weekly, or monthly with APScheduler
- **User-friendly CLI**: Simple commands for common operations
- **Web GUI**: Browser-based interface for non-technical users
- **Domain templates**: Automated creation of new domains with boilerplate code
- **Programmatic API**: Use the package as a library in your applications

## Quickstart

### Installation

1. Clone the repository:
    ```bash
    git clone <<repository_url>>
    cd functional_core_imperative_shell
    ```

2. Install dependencies with `uv`:
    ```bash
    uv sync
    ```

3. Install the package in development mode:
    ```bash
    pip install -e .
    ```

4. Optional: install pre-commit hooks:
    ```bash
    pre-commit install --hook-type pre-commit --hook-type commit-msg
    ```

### Command Line Interface

The package includes a user-friendly CLI for common operations:

```bash
# List available domains
python -m insert_package_name.cli list

# Run all domains
python -m insert_package_name.cli run

# Run specific domains (when implemented)
python -m insert_package_name.cli run --domain example_domain

# Validate configuration
python -m insert_package_name.cli validate

# Show configuration
python -m insert_package_name.cli config

# Create a new domain
python -m insert_package_name.cli create-domain my_new_domain

# Launch the web GUI
python -m insert_package_name.cli gui
```

### Programmatic API

Use the package programmatically in your applications:

```python
from insert_package_name.api import DataFlow, run_domains, list_domains

# Simple usage
run_domains()  # Run all domains

# Using the DataFlow class
df = DataFlow()
domains = df.domains()
df.with_domains(["example_domain"]).run()

# Convenience functions
domains = list_domains()
is_valid = df.validate()
```

### Creating a New Domain

1. Create a new domain with the CLI:
    ```bash
    python -m insert_package_name.cli create-domain my_domain
    ```

2. Customize the generated files:
   - `domains/my_domain/schemas.py`: Define your data schemas
   - `domains/my_domain/ops.py`: Implement your business logic
   - `domains/my_domain/pipeline.py`: Orchestrate your operations
   - `configs/domains/my_domain.yaml`: Configure inputs, outputs, and parameters

3. Test your domain:
    ```bash
    python -m insert_package_name.main
    ```

### Web GUI

For users who prefer a graphical interface, launch the web-based GUI:

```bash
python -m insert_package_name.cli gui
```

This starts a web server at `http://127.0.0.1:5000` where you can:

- **View available domains**: See all configured data processing domains
- **Configure runs**: Select which domains to execute
- **Monitor execution**: Watch real-time logs and status updates
- **Validate configuration**: Check that your setup is correct before running
- **Start/stop pipelines**: Control pipeline execution with simple buttons

The GUI is perfect for:
- Non-technical users who need to run pipelines
- Quick configuration validation
- Monitoring long-running processes
- Learning the available domains and their purposes

### Legacy Usage

For advanced usage with Hydra configuration overrides:

```bash
python -m insert_package_name.main
```

The example config reads from [data/silver](data/silver) and writes to [data/gold](data/gold). Adjust paths in [configs/config.yaml](configs/config.yaml) or override via Hydra.

## API Reference

### Command Line Interface

```bash
python -m insert_package_name.cli [OPTIONS] COMMAND [ARGS]

Options:
  --config-path TEXT  Path to config directory
  -v, --verbose       Enable verbose logging
  --help              Show this message and exit.

Commands:
  config         Show current configuration.
  create-domain  Create a new domain with template files.
  gui            Launch the web GUI for pipeline configuration and execution.
  list           List available domains.
  run            Run data pipelines.
  validate       Validate configuration without running.
```

### Programmatic API

#### DataFlow Class

```python
class DataFlow:
    def __init__(config_path=None)
    def domains() -> list[str]
    def with_domains(domains) -> DataFlow
    def with_config_overrides(overrides) -> DataFlow
    def run(domains=None) -> None
    def validate() -> bool
    def get_config() -> dict
```

#### Convenience Functions

```python
def run_domains(domains=None, config_path=None) -> None
def list_domains(config_path=None) -> list[str]
def validate_config(config_path=None) -> bool
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

Copy [./.env.example](.env.example) to [.env](.env) to provide environment variables used by overrides and configs.

## Secrets management

Secrets are injected via environment variables (for example using a [.env](.env) file). Use Hydra config values with env
interpolation to avoid committing secrets:

```yaml
# configs/domains/example_domain.yaml
example_domain:
  inputs:
    customers:
      path: ${oc.env:CUSTOMERS_PATH}
      format: csv
```

Then set the value in your [.env](.env) file (do not commit real secrets):

```bash
CUSTOMERS_PATH=/app/data/silver/customers.csv
```

### Running specific domains

Run specific domains by name:

```bash
# Run just the sales and finance domains
python -m insert_package_name.main active_domains=[sales,finance]

# Run a single domain
python -m insert_package_name.main active_domains=[example_domain]

# Run domains by tag
python -m insert_package_name.main active_tags=[daily]
```

### Override configuration

Change shared input paths at runtime:

```bash
python -m insert_package_name.main inputs.customers.path="data/customers.csv"
```

Change domain-specific outputs:

```bash
python -m insert_package_name.main domains.example_domain.outputs.scores.path="data/scores.csv"
```

Combine domain selection with overrides:

```bash
python -m insert_package_name.main active_domains=[sales,finance] base_output_path=/custom/gold
```

## Configuration Architecture

### Safe-Loading Pattern

The system uses an **iterative safe-loading pattern** where each domain config is loaded independently with error isolation. If a domain config has errors (syntax, missing files, validation issues), it's logged and skipped—allowing valid domains to execute successfully.

Benefits:
- **Resilience**: One broken config doesn't crash the entire batch
- **Visibility**: Clear logging shows which domains succeeded/failed
- **Flexibility**: Easy CLI overrides for domain selection

### Shared Inputs (DRY)

Inputs are defined once in `configs/inputs/` and referenced by name in domain configs:

```yaml
# configs/inputs/common.yaml
customers:
  path: ${base_input_path}/customers.csv
  format: csv
transactions:
  path: ${base_input_path}/transactions.csv
  format: csv
```

Domains select inputs by name:

```yaml
# configs/domains/example_domain.yaml
example_domain:
  inputs: [customers, transactions]  # Reference by name
  outputs:
    scores:
      path: ${base_output_path}/example_domain/scores.csv
      format: csv
```

Override shared inputs at the top level:

```bash
python -m insert_package_name.main inputs.customers.path=/custom/path.csv
```

### Schedule Presets

Schedule configurations are composable presets in `configs/schedule/`:

```yaml
# configs/schedule/daily.yaml
enabled: true
interval: "daily"
hour: 2
minute: 0
```

Domains reference them:

```yaml
defaults:
  - /schedule@example_domain.schedule: daily
```

### Batch Configurations

Batch configs in `configs/batch/` define which domains to run:

```yaml
# configs/batch/daily.yaml
domains_to_run:
  - example_domain
active_tags: ["daily"]
```

Run batches:

```bash
python -m insert_package_name.main batch=daily
```

## Scheduling

Configure domains to run automatically on a schedule:

```yaml
# configs/domains/example_domain.yaml
example_domain:
  schedule:
    enabled: true
    interval: "daily"  # daily, weekly, or monthly
    hour: 2  # 2:00 AM
    minute: 0
```

Start the scheduler:

```bash
python -m insert_package_name.scheduler_main
```

See [Scheduling Guide](docs/source/scheduling.md) for daily, weekly, monthly, and cron-based schedules.

## Configuration model

Hydra loads configs from [configs](configs):

- [configs/config.yaml](configs/config.yaml): top-level defaults.
- [configs/domains](configs/domains): per-domain inputs, outputs, and params.
- [configs/infrastructure](configs/infrastructure): logging and infrastructure settings.

Validated dataclasses live in `insert_package_name.schema.types` and are produced by `load_and_validate_config`.

## Create a new domain

To add a domain, create a pipeline module, add schemas, and wire config:

1. Add a domain folder under [src/insert_package_name/domains](src/insert_package_name/domains) with files like [src/insert_package_name/domains/example_domain/__init__.py](src/insert_package_name/domains/example_domain/__init__.py) and [src/insert_package_name/domains/example_domain/pipeline.py](src/insert_package_name/domains/example_domain/pipeline.py).
2. Implement a `run(cfg: DomainConfig)` entry point and optional schemas similar to [src/insert_package_name/domains/example_domain/schemas.py](src/insert_package_name/domains/example_domain/schemas.py).
3. Add a config file under [configs/domains](configs/domains) and include it in [configs/config.yaml](configs/config.yaml).

Minimal example:

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

See the [docs/source/user_guide.md](docs/source/user_guide.md) for more detail.

## IO formats

Readers and writers are registered in [src/insert_package_name/core/io.py](src/insert_package_name/core/io.py). Each IO config requires:

- `path`: local file path or URI.
- `format`: one of `csv`, `parquet`, `json`, `excel`, `feather`, `orc`, `pickle`, `sql`, `delta`.
- `options`: format-specific read/write options.
- `storage_options`: fsspec storage options.

Delta IO requires the `deltalake` optional dependency. SQL requires a SQLAlchemy-compatible URI and driver (for example `psycopg2` for Postgres).

See [IO Formats Reference](docs/source/io_formats.md) for a complete guide with examples for:
- **Cloud storage**: S3, Azure Blob Storage, Google Cloud Storage
- **Databases**: PostgreSQL, MySQL, Microsoft SQL Server
- **Data lakes**: Databricks, Delta Lake
- **Formats**: CSV, Parquet, JSON, Excel, SQL, and more

## Cloud deployment

### Databricks

Run on Databricks clusters with Unity Catalog tables:

```yaml
# configs/domains/example_domain.yaml
example_domain:
  inputs:
    customers:
      path: "databricks:///?host=${oc.env:DATABRICKS_HOST}&http_path=${oc.env:DATABRICKS_HTTP_PATH}&token=${oc.env:DATABRICKS_TOKEN}"
      format: sql
      options:
        query: "SELECT * FROM main.silver.customers"
```

### AWS S3

Read from and write to S3 buckets:

```yaml
example_domain:
  inputs:
    data:
      path: "s3://my-bucket/silver/data.parquet"
      format: parquet
      storage_options:
        client_kwargs:
          region_name: "us-east-1"
```

### Microsoft SQL Server

Connect to MSSQL databases (requires `pyodbc`):

```bash
uv add pyodbc
```

```yaml
example_domain:
  inputs:
    orders:
      path: "mssql+pyodbc://user:pass@server/db?driver=ODBC+Driver+17+for+SQL+Server"
      format: sql
      options:
        table: "dbo.orders"
```

## Development

Run tests:

```bash
python -m pytest -q
```

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run specific test modules
pytest tests/unit/test_cli.py
pytest tests/unit/test_api.py
pytest tests/unit/test_create_domain.py

# Run with coverage
pytest --cov=insert_package_name

# Run integration tests
pytest tests/integration/
```

### Code Quality

The project uses several tools for code quality:

- **ruff**: Linting and code formatting
- **mypy**: Type checking
- **bandit**: Security scanning

```bash
# Run all quality checks
ruff check src/
mypy src/
bandit -r src/
```

### Contributing

1. Create a new domain for your feature:
    ```bash
    python -m insert_package_name.cli create-domain my_feature
    ```

2. Implement your business logic in the generated files

3. Add tests for your new functionality

4. Run the test suite:
    ```bash
    pytest
    ```

5. Submit a pull request

## License

See [LICENSE](LICENSE).
