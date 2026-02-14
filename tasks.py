"""Provide utility functions to create documentation."""

import os

from invoke import Context, task

WINDOWS = os.name == "nt"
PROJECT_NAME = "insert_package_name"
PYTHON_VERSION = "3.13"


# Documentation commands
@task
def build_docs(ctx: Context) -> None:
    """Build documentation with Sphinx."""
    ctx.run("uv run sphinx-build -b html docs/source docs/_build/html", echo=True, pty=not WINDOWS)


@task
def serve_docs(ctx: Context) -> None:
    """Serve documentation."""
    ctx.run("uv run sphinx-build -b html docs/source docs/_build/html", echo=True, pty=not WINDOWS)
    ctx.run("uv run python -m http.server 8000 --directory docs/_build/html", echo=True, pty=not WINDOWS)
