"""Tests for the main entry point."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from insert_package_name.main import get_config_directory, load_domain_configs
from insert_package_name.main import main as hydra_main


class TestMain:
    """Test the main entry point functions."""

    def test_get_config_directory(self):
        """Test getting the config directory path."""
        from pathlib import Path

        import insert_package_name.configs

        expected = str(Path(insert_package_name.configs.__file__).parent)
        result = get_config_directory()
        assert result == expected
        assert Path(result).exists()

    @patch("insert_package_name.main.compose")
    @patch("insert_package_name.main.load_and_validate_config")
    def test_load_domain_configs_success(self, mock_validate, mock_compose):
        """Test successful domain config loading."""
        # Mock the compose function
        mock_cfg = MagicMock()
        mock_compose.return_value = mock_cfg

        # Mock the validation function
        mock_validated = MagicMock()
        mock_validated.domains = {"test_domain": MagicMock()}
        mock_validate.return_value = mock_validated

        # Mock logger
        mock_logger = MagicMock()

        domains_to_load = ["test_domain"]
        cli_overrides = []

        result = load_domain_configs(domains_to_load, cli_overrides, mock_logger)

        assert len(result) == 2  # (valid_configs, failed_domains)
        valid_configs, failed_domains = result
        assert len(valid_configs) == 1
        assert len(failed_domains) == 0
        assert valid_configs[0][0] == "test_domain"
        assert valid_configs[0][1] == mock_validated
        mock_logger.info.assert_called_with("[OK] Successfully loaded: test_domain")

    @patch("insert_package_name.main.compose")
    @patch("insert_package_name.main.load_and_validate_config")
    def test_load_domain_configs_domain_not_found(self, mock_validate, mock_compose):
        """Test domain config loading when domain is not in config."""
        # Mock the compose function
        mock_cfg = MagicMock()
        mock_compose.return_value = mock_cfg

        # Mock the validation function
        mock_validated = MagicMock()
        mock_validated.domains = {}  # Domain not found
        mock_validate.return_value = mock_validated

        # Mock logger
        mock_logger = MagicMock()

        domains_to_load = ["missing_domain"]
        cli_overrides = []

        result = load_domain_configs(domains_to_load, cli_overrides, mock_logger)

        assert len(result) == 2  # (valid_configs, failed_domains)
        valid_configs, failed_domains = result
        assert len(valid_configs) == 0
        assert len(failed_domains) == 1
        mock_logger.warning.assert_called_with("[SKIP] Domain 'missing_domain' not found in config")

    @patch("insert_package_name.main.compose")
    @patch("insert_package_name.main.load_and_validate_config")
    def test_load_domain_configs_validation_error(self, mock_validate, mock_compose):
        """Test domain config loading with validation error."""
        # Mock the compose function to raise an exception
        mock_compose.side_effect = ValueError("Invalid config")

        # Mock logger
        mock_logger = MagicMock()

        domains_to_load = ["bad_domain"]
        cli_overrides = []

        result = load_domain_configs(domains_to_load, cli_overrides, mock_logger)

        assert len(result) == 2  # (valid_configs, failed_domains)
        valid_configs, failed_domains = result
        assert len(valid_configs) == 0
        assert len(failed_domains) == 1
        mock_logger.error.assert_called_with("[FAIL] Failed to load 'bad_domain': Invalid config")

    @patch("insert_package_name.main.initialize_config_dir")
    @patch("insert_package_name.main.compose")
    @patch("insert_package_name.main.load_and_validate_config")
    @patch("insert_package_name.main.configure_logging")
    @patch("insert_package_name.main.get_logger")
    @patch("insert_package_name.main.run_domains_safe")
    def test_main_success_path(
        self, mock_run_domains, mock_get_logger, mock_configure_logging, mock_validate, mock_compose, mock_initialize
    ):
        """Test successful main execution path."""
        # Mock configuration
        mock_cfg = MagicMock()
        mock_cfg.get.return_value = ["example_domain"]
        mock_cfg.run_domains = None

        mock_schedule_cfg = MagicMock()
        mock_schedule_cfg.get.return_value = ["example_domain"]

        mock_compose.side_effect = [mock_schedule_cfg, mock_cfg]

        # Mock validation
        mock_validated = MagicMock()
        mock_validated.domains = {"example_domain": MagicMock()}
        mock_validate.return_value = mock_validated

        # Mock logger
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger

        # Call main function
        hydra_main(mock_cfg)

        # Verify calls
        mock_initialize.assert_called_once()
        mock_configure_logging.assert_called_once()
        mock_run_domains.assert_called_once()

    @patch("insert_package_name.main.initialize_config_dir")
    @patch("insert_package_name.main.compose")
    @patch("insert_package_name.main.load_and_validate_config")
    @patch("insert_package_name.main.configure_logging")
    @patch("insert_package_name.main.get_logger")
    def test_main_with_domains_to_run(
        self, mock_get_logger, mock_configure_logging, mock_validate, mock_compose, mock_initialize
    ):
        """Test main execution with domains_to_run specified."""
        # Mock configuration
        mock_cfg = MagicMock()

        mock_schedule_cfg = MagicMock()
        mock_schedule_cfg.get.return_value = ["specified_domain"]  # domains_to_run
        mock_compose.return_value = mock_schedule_cfg

        # Mock validation
        mock_validated = MagicMock()
        mock_validated.domains = {"specified_domain": MagicMock()}
        mock_validate.return_value = mock_validated

        # Mock logger
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger

        # Call main function
        hydra_main(mock_cfg)

        # Verify domains_to_run was used
        mock_logger.info.assert_any_call("Attempting to load 1 domain(s)")

    @patch("insert_package_name.main.initialize_config_dir")
    @patch("insert_package_name.main.compose")
    @patch("insert_package_name.main.load_and_validate_config")
    @patch("insert_package_name.main.configure_logging")
    def test_main_no_valid_configs(self, mock_configure_logging, mock_validate, mock_compose, mock_initialize):
        """Test main execution when no valid configs are found."""
        # Mock configuration
        mock_cfg = MagicMock()
        mock_cfg.get.return_value = ["missing_domain"]

        mock_schedule_cfg = MagicMock()
        mock_schedule_cfg.get.return_value = ["missing_domain"]
        mock_compose.return_value = mock_schedule_cfg

        # Mock validation - domain not found
        mock_validated = MagicMock()
        mock_validated.domains = {}
        mock_validate.return_value = mock_validated

        # This should not raise an exception, just log and exit gracefully
        with patch("insert_package_name.main.get_logger") as mock_get_logger:
            mock_logger = MagicMock()
            mock_get_logger.return_value = mock_logger

            hydra_main(mock_cfg)

            mock_logger.error.assert_called_with("No valid configurations. Exiting.")

    @patch("insert_package_name.main.initialize_config_dir")
    @patch("insert_package_name.main.compose")
    def test_main_setup_error(self, mock_compose, mock_initialize):
        """Test main execution with setup error."""
        # Mock compose to raise an exception during initial setup
        mock_compose.side_effect = Exception("Setup failed")

        mock_cfg = MagicMock()

        with patch("builtins.print") as mock_print:
            with pytest.raises(Exception, match="Setup failed"):
                hydra_main(mock_cfg)

            # Should print error
            mock_print.assert_called()
