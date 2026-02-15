"""Tests for the CLI interface."""

from __future__ import annotations

from unittest.mock import patch

import pytest

from insert_package_name.cli import cli


class TestCLI:
    """Test the CLI interface."""

    def test_cli_help(self, capsys):
        """Test CLI help output."""
        with pytest.raises(SystemExit):
            cli(["--help"])

    def test_cli_list_command(self, capsys):
        """Test the list command."""
        with pytest.raises(SystemExit):
            cli(["list"])
        captured = capsys.readouterr()
        assert "Available domains:" in captured.out
        assert "example_domain" in captured.out

    def test_cli_config_command(self, capsys):
        """Test the config command."""
        with pytest.raises(SystemExit):
            cli(["config"])
        captured = capsys.readouterr()
        assert "Configuration:" in captured.out
        assert "Config path:" in captured.out

    def test_cli_validate_command(self, capsys):
        """Test the validate command."""
        with pytest.raises(SystemExit):
            cli(["validate"])
        captured = capsys.readouterr()
        assert "[OK] Configuration appears valid" in captured.out

    @patch("subprocess.run")
    def test_cli_run_command(self, mock_subprocess, capsys):
        """Test the run command."""
        mock_subprocess.return_value.returncode = 0
        with pytest.raises(SystemExit):
            cli(["run"])
        captured = capsys.readouterr()
        # Should not output anything on success
        mock_subprocess.assert_called_once()

    @patch("subprocess.run")
    def test_cli_run_dry_run(self, mock_subprocess, capsys):
        """Test the run command with dry-run."""
        with pytest.raises(SystemExit):
            cli(["run", "--dry-run"])
        captured = capsys.readouterr()
        assert "Would run all domains" in captured.out
        mock_subprocess.assert_not_called()

    def test_cli_create_domain_command(self, tmp_path, capsys):
        """Test the create-domain command."""
        # Change to tmp_path for testing
        with patch("insert_package_name.cli.get_config_directory", return_value=str(tmp_path)):
            with pytest.raises(SystemExit):
                cli(["create-domain", "test_domain", "--target-dir", str(tmp_path)])

        captured = capsys.readouterr()
        assert "Creating domain 'test_domain'..." in captured.out
        assert "[OK] Created domain code" in captured.out
        assert "[OK] Created domain config" in captured.out

        # Check that files were created
        domain_dir = tmp_path / "domains" / "test_domain"
        assert domain_dir.exists()
        assert (domain_dir / "__init__.py").exists()
        assert (domain_dir / "ops.py").exists()
        assert (domain_dir / "pipeline.py").exists()
        assert (domain_dir / "schemas.py").exists()

        config_dir = tmp_path / "domains"
        assert (config_dir / "test_domain.yaml").exists()

    def test_cli_verbose_option(self, capsys):
        """Test the verbose option."""
        with patch("insert_package_name.cli.configure_logging") as mock_configure:
            with pytest.raises(SystemExit):
                cli(["--verbose", "list"])
            mock_configure.assert_called()

    def test_cli_config_path_option(self, capsys):
        """Test the config-path option."""
        with patch("insert_package_name.cli.get_config_directory", return_value="/custom/path"):
            with pytest.raises(SystemExit):
                cli(["--config-path", "/custom/path", "config"])
            captured = capsys.readouterr()
            assert "/custom/path" in captured.out
