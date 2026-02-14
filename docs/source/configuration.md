# Configuration Guide

This guide explains the Hydra configuration architecture, including the safe-loading pattern, shared inputs, schedule presets, and batch configurations.

## Overview

The configuration system is built on **Hydra** with three key innovations:

1. **Safe-Loading Pattern**: Domains are loaded iteratively with error isolation
2. **Shared Inputs (DRY)**: Common inputs are defined once and referenced by name
3. **Composable Presets**: Schedule and batch configs are reusable components

## Configuration Structure

```
configs/
├── config.yaml              # Main config with defaults
├── batch/                   # Batch run configurations
│   ├── daily.yaml
│   └── monthly.yaml
├── domains/                 # Per-domain configs
│   └── example_domain.yaml
├── inputs/                  # Shared input definitions
│   └── common.yaml
├── schedule/                # Schedule presets
│   ├── disabled.yaml
│   ├── daily.yaml
│   ├── monthly.yaml
│   └── cron_complex.yaml
└── infrastructure/          # Infrastructure configs
    └── logging.yaml
```

## Safe-Loading Pattern

### What It Solves

Traditional Hydra configs fail completely if **any** domain has errors. The safe-loading pattern isolates errors:

- Each domain config is loaded independently inside a try-catch block
- Broken configs are logged and skipped
- Valid domains execute successfully
- The batch continues even if some domains fail

### How It Works

The main entry point (`main.py`) uses `hydra.compose()` to load each domain individually:

```python
for domain_name in domains_to_load:
    try:
        domain_cfg = compose(config_name="config", overrides=[f"+domain={domain_name}"])
        validated = load_and_validate_config(domain_cfg)
        valid_configs.append((domain_name, validated))
    except Exception as exc:
        logger.error(f"Failed to load config for domain '{domain_name}': {exc}")
        failed_domains.append(domain_name)
```

### Benefits

- **Resilience**: One broken config doesn't crash the entire pipeline
- **Visibility**: Clear logging shows which domains succeeded/failed during config loading
- **Debugging**: Failed domains are reported with full error messages
- **Production Safety**: Critical domains can run even if experimental ones are broken

## Shared Inputs (DRY Principle)

### Problem

Without shared inputs, every domain duplicates input definitions:

```yaml
# ❌ Duplicated in every domain
domain_a:
  inputs:
    customers:
      path: /data/silver/customers.csv
      format: csv

domain_b:
  inputs:
    customers:
      path: /data/silver/customers.csv  # Duplicate!
      format: csv
```

This violates DRY and makes updates error-prone.

### Solution

Define inputs once in `configs/inputs/`:

```yaml
# configs/inputs/common.yaml
customers:
  path: ${base_input_path}/customers.csv
  format: csv
transactions:
  path: ${base_input_path}/transactions.csv
  format: csv
products:
  path: ${base_input_path}/products.csv
  format: csv
```

Load shared inputs globally in `configs/config.yaml`:

```yaml
defaults:
  - infrastructure/logging@logging
  - inputs@inputs: common  # ✅ Shared inputs loaded here
  - domains:
      - example_domain
  - _self_
```

Reference inputs by name in domain configs:

```yaml
# configs/domains/example_domain.yaml
example_domain:
  inputs: [customers, transactions]  # ✅ Reference by name
  outputs:
    scores:
      path: ${base_output_path}/example_domain/scores.csv
      format: csv
```

### Creating Input Groups

Create specialized input groups for different domain types:

```yaml
# configs/inputs/finance.yaml
accounts:
  path: ${base_input_path}/accounts.csv
  format: csv
ledger:
  path: ${base_input_path}/ledger.csv
  format: parquet
```

Reference in domain:

```yaml
# configs/domains/finance_domain.yaml
defaults:
  - /inputs@finance_domain.inputs: finance
```

### Overriding Shared Inputs

Override shared inputs at the top level (affects all domains):

```bash
python -m insert_package_name.main inputs.customers.path=/custom/customers.csv
```

This changes the `customers` input for **all domains** that reference it.

## Schedule Presets

### Available Presets

Schedule presets live in `configs/schedule/`:

**Disabled (default)**:
```yaml
# configs/schedule/disabled.yaml
enabled: false
```

**Daily at 2 AM**:
```yaml
# configs/schedule/daily.yaml
enabled: true
interval: "daily"
hour: 2
minute: 0
```

**Monthly on the 1st at 2 AM**:
```yaml
# configs/schedule/monthly.yaml
enabled: true
interval: "monthly"
day_of_month: 1
hour: 2
minute: 0
```

**Complex Cron Expression**:
```yaml
# configs/schedule/cron_complex.yaml
enabled: true
cron: "15 2 * * 1-5"  # 2:15 AM on weekdays
```

### Using Schedule Presets

Reference in domain defaults:

```yaml
# configs/domains/example_domain.yaml
defaults:
  - /schedule@example_domain.schedule: daily  # Uses daily preset
  - _self_

example_domain:
  name: "Example Domain"
  inputs: [customers, transactions]
  outputs: { ... }
```

### Creating Custom Schedules

Add a new preset in `configs/schedule/`:

```yaml
# configs/schedule/quarterly.yaml
enabled: true
interval: "monthly"
day_of_month: 1
hour: 3
minute: 0
# Run every 3 months by filtering in scheduling logic or using cron
```

See [Scheduling](scheduling.md) for full schedule configuration details.

## Batch Configurations

### What Are Batches?

Batch configs define **which domains to run** for scheduled or manual batch jobs.

### Structure

```yaml
# configs/batch/daily.yaml
domains_to_run:
  - example_domain
  - sales_domain
  - marketing_domain
active_tags: ["daily"]
```

### Running Batches

Run a batch via CLI:

```bash
python -m insert_package_name.main batch=daily
```

This:
1. Loads the `batch/daily.yaml` config
2. Attempts to load all domains in `domains_to_run`
3. Filters by `active_tags` if specified
4. Executes valid domains with error isolation

### Multiple Batches

Create different batches for different schedules:

```yaml
# configs/batch/monthly.yaml
domains_to_run:
  - monthly_summary
  - quarterly_report
active_tags: ["monthly"]
```

```yaml
# configs/batch/adhoc.yaml
domains_to_run:
  - data_audit
  - compliance_check
active_tags: []
```

Run them:

```bash
python -m insert_package_name.main batch=monthly
python -m insert_package_name.main batch=adhoc
```

## Main Configuration File

The `configs/config.yaml` sets global defaults:

```yaml
defaults:
  - infrastructure/logging@logging  # Load logging config
  - inputs@inputs: common            # Load shared inputs
  - domains:                         # Load domain configs
      - example_domain
  - _self_

env: dev
active_domains: []  # Filter by domain name
active_tags: []     # Filter by tags

# Optional: explicit domain list for safe-loading
domains_to_run: []

# Base paths for all IO
base_input_path: ${hydra:runtime.cwd}/data/silver
base_output_path: ${hydra:runtime.cwd}/data/gold
```

### Key Fields

- **`active_domains`**: List of domain names to execute (empty = all)
- **`active_tags`**: List of tags to filter domains (empty = all)
- **`domains_to_run`**: Explicit list for safe-loading (empty = use defaults)
- **`base_input_path`**: Root path for silver inputs
- **`base_output_path`**: Root path for gold outputs

### CLI Overrides

Override any field at runtime:

```bash
# Run specific domains (most common pattern)
python -m insert_package_name.main active_domains=[sales,finance]

# Run a single domain
python -m insert_package_name.main active_domains=[example_domain]

# Filter by tags
python -m insert_package_name.main active_tags=[daily]

# Run domains with multiple tags (matches any)
python -m insert_package_name.main active_tags=[critical,daily]

# Change base paths
python -m insert_package_name.main base_input_path=/custom/silver

### Combine domain selection with overrides
python -m insert_package_name.main active_domains=[sales,finance] base_output_path=/custom/gold
```

## Domain Selection Patterns

### Select domains by name

The most common pattern is selecting specific domains by name:

```bash
# Run just sales and finance domains
python -m insert_package_name.main active_domains=[sales,finance]

# Run a single domain for testing
python -m insert_package_name.main active_domains=[example_domain]

# Run many domains at once
python -m insert_package_name.main active_domains=[sales,finance,marketing,hr,operations]
```

**When to use**: Ad-hoc runs, testing specific domains, manual execution.

### Select domains by tags

Filter domains using tags defined in domain configs:

```bash
# Run all domains tagged as "daily"
python -m insert_package_name.main active_tags=[daily]

# Run all critical domains
python -m insert_package_name.main active_tags=[critical]

# Run domains with either "daily" OR "critical" tag
python -m insert_package_name.main active_tags=[daily,critical]
```

**When to use**: Scheduled batch jobs, consistent groupings, production runs.

**Important**: `active_tags` uses OR logic—a domain runs if it has ANY of the listed tags.

### Combine selection methods

You can also combine name and tag filters (both must match):

```bash
# Run finance domain if it has the "daily" tag
python -m insert_package_name.main active_domains=[finance] active_tags=[daily]
```

**Note**: When both are specified, a domain must match BOTH filters to run.

### Run all domains

Omit filters to run all enabled domains:

```bash
python -m insert_package_name.main
```

This runs every domain where `enabled: true` in their config.

## Domain Configuration

### Minimal Domain Config

```yaml
# configs/domains/minimal.yaml
minimal:
  name: "Minimal Domain"
  enabled: true
  inputs: [customers]
  outputs:
    result:
      path: ${base_output_path}/minimal/result.csv
      format: csv
```

### Full Domain Config

```yaml
# configs/domains/full_example.yaml
defaults:
  - /schedule@full_example.schedule: daily
  - _self_

full_example:
  name: "Full Example"
  enabled: true
  tags: ["daily", "critical"]
  inputs: [customers, transactions, products]
  params:
    threshold: 0.8
    window_days: 30
  outputs:
    scores:
      path: ${base_output_path}/full_example/scores.parquet
      format: parquet
      options:
        compression: snappy
    metrics:
      path: ${base_output_path}/full_example/metrics.csv
      format: csv
```

### Domain Fields

- **`name`**: Display name for logging
- **`enabled`**: Whether domain is active (default: `true`)
- **`tags`**: List of tags for filtering
- **`inputs`**: List of input names (references shared inputs)
- **`outputs`**: Dict of output names to IO configs
- **`params`**: Domain-specific parameters
- **`schedule`**: Schedule config (loaded via defaults)

## Override Patterns

### Override Shared Inputs

Affects all domains using the input:

```bash
python -m insert_package_name.main inputs.customers.path=/new/customers.csv
```

### Override Domain Outputs

Affects only the specific domain:

```bash
python -m insert_package_name.main domains.example_domain.outputs.scores.path=/custom/scores.csv
```

### Override Domain Parameters

```bash
python -m insert_package_name.main domains.example_domain.params.score_threshold=0.9
```

### Disable a Domain

```bash
python -m insert_package_name.main domains.example_domain.enabled=false
```

### Change Schedule

```bash
python -m insert_package_name.main domains.example_domain.schedule.enabled=true
```

## Environment Variables

Use environment variables with Hydra's `oc.env` resolver:

```yaml
# configs/domains/example_domain.yaml
example_domain:
  outputs:
    scores:
      path: ${oc.env:OUTPUT_PATH,${base_output_path}/example_domain/scores.csv}
      format: csv
```

Set in `.env` file:

```bash
OUTPUT_PATH=/custom/path/scores.csv
```

The second argument to `oc.env` is the default if the variable is not set.

## Best Practices

### 1. Use Shared Inputs

Define common inputs once in `configs/inputs/common.yaml` and reference by name.

### 2. Tag Your Domains

Use consistent tags for filtering:

```yaml
tags: ["daily", "critical", "finance"]
```

### 3. Use Batch Configs for Scheduled Jobs

Create batch configs for cron jobs or cloud schedulers:

```bash
# In crontab or cloud scheduler
0 2 * * * python -m insert_package_name.main batch=daily
```

### 4. Keep Domain Configs Small

Let Hydra composition do the work:

```yaml
# ✅ Good: use shared inputs and schedule presets
defaults:
  - /schedule@marketing.schedule: daily

marketing:
  inputs: [customers, sales]
  outputs: { ... }
```

```yaml
# ❌ Bad: duplicate everything
marketing:
  schedule:
    enabled: true
    interval: daily
    hour: 2
  inputs:
    customers:
      path: /data/customers.csv  # Duplicated!
```

### 5. Test Config Changes

Check the effective config before running:

```bash
python -m insert_package_name.main --cfg job
```

### 6. Use Explicit Batches in Production

Prefer explicit `domains_to_run` lists in production batch configs for predictability:

```yaml
# configs/batch/production_daily.yaml
domains_to_run:
  - finance_etl
  - sales_summary
  - marketing_metrics
active_tags: []  # Don't rely on tags in production
```

## Troubleshooting

### Domain Not Loading

Check logs for `[FAIL]` messages:

```
INFO [-] [FAIL] Failed to load config for domain 'broken_domain': ...
```

Fix the config error and rerun.

### Input Not Found

Error: `Domain 'example' references unknown inputs: customers`

Solution: Add the input to `configs/inputs/common.yaml` or the referenced input group.

### Override Not Working

Ensure you're using the correct path:

- Shared inputs: `inputs.customers.path=...`
- Domain outputs: `domains.example_domain.outputs.scores.path=...`

Use `--cfg job` to verify the effective config.

## See Also

- [Getting Started](getting_started.md) - Quick setup guide
- [User Guide](user_guide.md) - Architecture overview
- [Scheduling](scheduling.md) - Automatic schedule configuration
- [Examples](examples.md) - Copy-paste config examples
