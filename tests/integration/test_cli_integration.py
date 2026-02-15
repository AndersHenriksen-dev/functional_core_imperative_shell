"""Integration tests for CLI functionality."""

from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path


class TestCLIIntegration:
    """Integration tests for CLI commands."""

    def test_cli_list_integration(self):
        """Test CLI list command end-to-end."""
        result = subprocess.run(
            [sys.executable, "-m", "insert_package_name.cli", "list"], capture_output=True, text=True, cwd=Path.cwd()
        )
        assert result.returncode == 0
        assert "Available domains:" in result.stdout
        assert "example_domain" in result.stdout

    def test_cli_validate_integration(self):
        """Test CLI validate command end-to-end."""
        result = subprocess.run(
            [sys.executable, "-m", "insert_package_name.cli", "validate"],
            capture_output=True,
            text=True,
            cwd=Path.cwd(),
        )
        assert result.returncode == 0
        assert "[OK] Configuration appears valid" in result.stdout

    def test_cli_config_integration(self):
        """Test CLI config command end-to-end."""
        result = subprocess.run(
            [sys.executable, "-m", "insert_package_name.cli", "config"], capture_output=True, text=True, cwd=Path.cwd()
        )
        assert result.returncode == 0
        assert "Configuration:" in result.stdout
        assert "Config path:" in result.stdout

    def test_cli_create_domain_integration(self):
        """Test CLI create-domain command end-to-end."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "insert_package_name.cli",
                    "create-domain",
                    "integration_test_domain",
                    "--target-dir",
                    tmp_dir,
                    "--config-dir",
                    tmp_dir,
                ],
                capture_output=True,
                text=True,
                cwd=Path.cwd(),
            )
            assert result.returncode == 0
            assert "Creating domain 'integration_test_domain'..." in result.stdout
            assert "[OK] Created domain code" in result.stdout
            assert "[OK] Created domain config" in result.stdout

            # Verify files were created
            domain_dir = Path(tmp_dir) / "domains" / "integration_test_domain"
            assert domain_dir.exists()
            assert (domain_dir / "ops.py").exists()
            assert (domain_dir / "pipeline.py").exists()
            assert (domain_dir / "schemas.py").exists()

            config_file = Path(tmp_dir) / "domains" / "integration_test_domain.yaml"
            assert config_file.exists()

    def test_cli_run_dry_run_integration(self):
        """Test CLI run --dry-run command end-to-end."""
        result = subprocess.run(
            [sys.executable, "-m", "insert_package_name.cli", "run", "--dry-run"],
            capture_output=True,
            text=True,
            cwd=Path.cwd(),
        )
        assert result.returncode == 0
        assert "Would run all domains" in result.stdout

    def test_cli_help_integration(self):
        """Test CLI help command end-to-end."""
        result = subprocess.run(
            [sys.executable, "-m", "insert_package_name.cli", "--help"], capture_output=True, text=True, cwd=Path.cwd()
        )
        assert result.returncode == 0
        assert "Data pipeline orchestration tool" in result.stdout
        assert "Commands:" in result.stdout
        assert "list" in result.stdout
        assert "run" in result.stdout
        assert "validate" in result.stdout
