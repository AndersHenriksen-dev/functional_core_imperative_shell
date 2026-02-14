# Getting Started

This page covers a quick setup and the shortest path to a successful run.

## Install

```bash
uv sync
```

## Run the default pipeline

The default configuration runs the example domain pipeline.

```bash
python -m insert_package_name.main
```

## Run specific domains

You can run specific domains by name without any batch configuration:

```bash
# Run a single domain
python -m insert_package_name.main active_domains=[example_domain]

# Run multiple specific domains
python -m insert_package_name.main active_domains=[sales,finance]

# Run three specific domains
python -m insert_package_name.main active_domains=[sales,finance,marketing]
```

## Filter domains by tags

You can filter which domains run using tags:

```bash
# Run all domains tagged as "daily"
python -m insert_package_name.main active_tags=[daily]

# Run domains with "critical" tag
python -m insert_package_name.main active_tags=[critical]

# Run domains matching multiple tags (any match)
python -m insert_package_name.main active_tags=[daily,critical]
```

## Override configuration values

Override config values at runtime:

```bash
# Run specific domains (most common)
python -m insert_package_name.main active_domains=[sales,finance]

# Change a shared input path
python -m insert_package_name.main inputs.customers.path="data/customers.csv"

# Change an output path
python -m insert_package_name.main domains.example_domain.outputs.scores.path="outputs/scores.csv"

# Update a domain parameter
python -m insert_package_name.main domains.example_domain.params.score_threshold=0.8

# Combine domain selection with overrides
python -m insert_package_name.main active_domains=[sales,finance] base_output_path=/custom/gold
```

## Inspect the effective config

If you are not sure which values are active, Hydra can render the full config:

```bash
python -m insert_package_name.main --cfg job
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

## Next steps

- Read the [User Guide](user_guide.md) for architecture and extension points.
- Use the [Examples](examples.md) page for copy-paste snippets.
- See [Scheduling](scheduling.md) to run domains on automatic schedules (daily, weekly, monthly).

## New domain checklist

- Create a domain module under [src/insert_package_name/domains/example_domain/pipeline.py](../../src/insert_package_name/domains/example_domain/pipeline.py).
- Add optional schemas under [src/insert_package_name/domains/example_domain/schemas.py](../../src/insert_package_name/domains/example_domain/schemas.py).
- Add a config file under [configs/domains](../../configs/domains) and include it in [configs/config.yaml](../../configs/config.yaml).
- Run the domain directly with `python -m insert_package_name.main active_domains=[your_domain]`.

Add your domain to the defaults list in [configs/config.yaml](../../configs/config.yaml):

```yaml
# configs/config.yaml
defaults:
  - infrastructure/logging@logging
  - inputs@inputs: common
  - domains:
      - example_domain
      - your_domain
  - _self_
```

If your domain uses shared inputs, reference them by name:

```yaml
# configs/domains/your_domain.yaml
your_domain:
  inputs: [customers, transactions]
  outputs:
    results:
      path: ${base_output_path}/your_domain/results.csv
      format: csv
```
