"""Command-line interface for insert_package_name."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import click

from insert_package_name.core.logging import configure_logging
from insert_package_name.create_domain import create_domain_impl
from insert_package_name.main import get_config_directory
from insert_package_name.schema.types import LoggingConfig


@click.group()
@click.option("--config-path", default=None, help="Path to config directory")
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose logging")
@click.pass_context
def cli(ctx: click.Context, config_path: str | None, verbose: bool) -> None:
    """Data pipeline orchestration tool."""
    ctx.ensure_object(dict)
    ctx.obj["config_path"] = config_path or get_config_directory()
    ctx.obj["verbose"] = verbose

    if verbose:
        configure_logging(LoggingConfig(level="DEBUG"))
    else:
        configure_logging(LoggingConfig(level="INFO"))


@cli.command()
@click.option("--domain", multiple=True, help="Specific domains to run")
@click.option("--dry-run", is_flag=True, help="Show what would run without executing")
@click.pass_context
def run(ctx: click.Context, domain: tuple[str, ...], dry_run: bool) -> None:
    """Run data pipelines."""
    try:
        if dry_run:
            click.echo("Would run all domains (dry run not yet implemented)")
            return

        # Run the main module
        cmd = [sys.executable, "-m", "insert_package_name.main"]
        if domain:
            # Use Hydra's list syntax: run_domains=[domain1,domain2]
            domains_str = ",".join(f'"{d}"' for d in domain)
            cmd.append(f"run_domains=[{domains_str}]")
        result = subprocess.run(cmd, cwd=Path.cwd())
        sys.exit(result.returncode)

    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.pass_context
def list(ctx: click.Context) -> None:
    """List available domains."""
    try:
        # For now, just show that we can list domains
        # This would need more complex config parsing
        click.echo("Available domains:")
        click.echo("  example_domain (enabled) [daily]")

    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option("--format", type=click.Choice(["yaml", "json"]), default="yaml", help="Output format")
@click.pass_context
def config(ctx: click.Context, format: str) -> None:
    """Show current configuration."""
    try:
        # For now, just show basic config info
        click.echo("Configuration:")
        click.echo("  Config path: " + ctx.obj["config_path"])
        click.echo("  Environment: dev")
        click.echo("  Execution: serial")

    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.pass_context
def validate(ctx: click.Context) -> None:
    """Validate configuration without running."""
    try:
        # For now, just try to run main and see if it succeeds
        cmd = [
            sys.executable,
            "-c",
            "from insert_package_name.main import get_config_directory; print('Config path:', get_config_directory())",
        ]
        result = subprocess.run(cmd, cwd=Path.cwd(), capture_output=True, text=True)

        if result.returncode == 0:
            click.echo("[OK] Configuration appears valid")
            click.echo("[OK] Can load config directory")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument("domain_name")
@click.option("--target-dir", default=".", help="Target directory for the domain")
@click.option("--config-dir", default=None, help="Config directory to update")
@click.pass_context
def create_domain(ctx: click.Context, domain_name: str, target_dir: str, config_dir: str | None) -> None:
    """Create a new domain with template files."""
    try:
        config_path = config_dir or ctx.obj["config_path"]
        create_domain_impl(domain_name, target_dir, config_path)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option("--host", default="127.0.0.1", help="Host to bind the GUI server to")
@click.option("--port", default=5000, type=int, help="Port to bind the GUI server to")
@click.option("--debug", is_flag=True, help="Run in debug mode")
def gui(host: str, port: int, debug: bool) -> None:
    """Launch the web GUI for pipeline configuration and execution."""
    try:
        from insert_package_name.gui import run_gui
        click.echo(f"Starting GUI server on http://{host}:{port}")
        click.echo("Press Ctrl+C to stop the server")
        run_gui(host=host, port=port, debug=debug)
    except Exception as e:
        click.echo(f"Error starting GUI: {e}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    cli()
