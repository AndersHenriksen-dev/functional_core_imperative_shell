# Scheduling Domain Pipelines

This guide explains how to automatically schedule domain pipelines to run on a fixed schedule (daily, weekly, monthly).

## Overview

The scheduler uses APScheduler to execute domains on specified schedules. Each domain can be configured with:

- **Interval**: "daily", "weekly", or "monthly"
- **Time**: hour (0-23) and minute (0-59)
- **Day** (for weekly/monthly): day of week or day of month
- **Cron expression** (optional): explicit cron syntax for complex schedules

## Basic configuration

Enable scheduling in a domain config file:

```yaml
# configs/domains/example_domain.yaml
example_domain:
  name: "Example Domain"
  enabled: true
  schedule:
    enabled: true  # Enable scheduling
    interval: "daily"
    hour: 2  # Run at 2:00 AM
    minute: 0
  inputs: { ... }
  outputs: { ... }
```

## Daily schedules

Run every day at a specified time:

```yaml
schedule:
  enabled: true
  interval: "daily"
  hour: 14  # 2:00 PM
  minute: 30
```

This runs the domain at 2:30 PM every day.

## Weekly schedules

Run once per week on a specified day and time:

```yaml
schedule:
  enabled: true
  interval: "weekly"
  day_of_week: "monday"  # Or "tuesday", "wednesday", ... "sunday"
  hour: 9
  minute: 0
```

This runs the domain every Monday at 9:00 AM.

Available days: `monday`, `tuesday`, `wednesday`, `thursday`, `friday`, `saturday`, `sunday`.

## Monthly schedules

Run once per month on a specified day and time:

```yaml
schedule:
  enabled: true
  interval: "monthly"
  day_of_month: 15  # Run on the 15th of each month
  hour: 3  # 3:00 AM
  minute: 0
```

This runs the domain on the 15th of every month at 3:00 AM.

## Cron expressions (advanced)

For complex schedules, use cron expressions directly:

```yaml
schedule:
  enabled: true
  cron: "0 2 * * *"  # 2:00 AM every day
```

### Common cron patterns

```yaml
# Every day at 2:00 AM
cron: "0 2 * * *"

# Every weekday (Monday-Friday) at 9:00 AM
cron: "0 9 * * 1-5"

# First and 15th of each month at 3:00 AM
cron: "0 3 1,15 * *"

# Every 6 hours
cron: "0 */6 * * *"

# Every Sunday at midnight
cron: "0 0 * * 0"

# Every weekday at 8:30 AM and 5:30 PM
cron: "30 8,17 * * 1-5"
```

Cron format: `minute hour day month day_of_week`

## Running the scheduler

Start the scheduler process:

```bash
python -m insert_package_name.scheduler_main
```

The scheduler will:

1. Load the global configuration
2. Identify all domains with `schedule.enabled: true`
3. Start a background scheduler with all configured jobs
4. Keep running and execute domains on their schedule

Press `Ctrl+C` to stop.

## Multiple scheduled domains

You can have multiple domains on different schedules:

```yaml
# configs/domains/daily_etl.yaml
daily_etl:
  enabled: true
  schedule:
    enabled: true
    interval: "daily"
    hour: 2
    minute: 0
  inputs: { ... }
  outputs: { ... }

# configs/domains/monthly_summary.yaml
monthly_summary:
  enabled: true
  schedule:
    enabled: true
    interval: "monthly"
    day_of_month: 1
    hour: 4
    minute: 0
  inputs: { ... }
  outputs: { ... }
```

When you run the scheduler:

```bash
python -m insert_package_name.scheduler_main
```

Both domains will execute on their respective schedules.

## Docker deployment

To run scheduled pipelines in Docker, build the wheel and create a container:

```dockerfile
FROM python:3.13-slim

WORKDIR /app
COPY dist/insert_package_name*.whl .
RUN pip install insert_package_name*.whl

# Run as a scheduled service
CMD ["python", "-m", "insert_package_name.scheduler_main"]
```

Build and run:

```bash
uv build
docker build -t data-handler-scheduler .
docker run --rm -it data-handler-scheduler
```

## Cloud scheduling (alternative)

For cloud platforms, you can instead:

1. Run `python -m insert_package_name.main active_domains=[domain_name]` via:
   - **Databricks**: Jobs scheduler
   - **AWS**: Lambda + EventBridge, or Step Functions
   - **GitHub Actions**: Scheduled workflows
   - **Airflow**: Managed DAGs

This gives you more control and monitoring in the cloud platform's native scheduler.

## Troubleshooting

### Domain doesn't run

Check that:
1. `schedule.enabled: true` is set in the domain config
2. `interval` is one of: "daily", "weekly", "monthly" (or `cron` is valid)
3. If using `interval` without `cron`, ensure `hour` and `minute` are 0-23 and 0-59
4. Domain has `enabled: true`
5. Run `python -m insert_package_name.scheduler_main` (scheduler must be running)

### Check scheduled jobs

The scheduler logs on startup which jobs were registered:

```
Scheduled domain 'daily_etl' with trigger: cron[minute='0', hour='2', day='*', month='*', day_of_week='*', second='0']
Scheduled domain 'monthly_summary' with trigger: cron[minute='0', hour='4', day='1', month='*', day_of_week='*', second='0']
Scheduler started with 2 scheduled domain(s)
```

### Time zone issues

The scheduler uses the system's local timezone. To use UTC:

Edit `scheduler_main.py` and set the scheduler timezone:

```python
from pytz import UTC

scheduler = BackgroundScheduler(timezone=UTC)
```

## See also

- [Hydra configuration documentation](https://hydra.cc/)
- [APScheduler documentation](https://apscheduler.readthedocs.io/)
- [Cron expression reference](https://en.wikipedia.org/wiki/Cron)
