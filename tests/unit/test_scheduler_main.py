"""Tests for the scheduler main entry point."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from insert_package_name.scheduler_main import main as scheduler_main


class TestSchedulerMain:
    """Test the scheduler main entry point."""

    @patch("insert_package_name.scheduler_main.load_and_validate_config")
    @patch("insert_package_name.scheduler_main.configure_logging")
    @patch("insert_package_name.scheduler_main.schedule_domains")
    @patch("insert_package_name.scheduler_main.logger")
    def test_scheduler_main_success(self, mock_logger, mock_schedule_domains, mock_configure_logging, mock_validate):
        """Test successful scheduler main execution."""
        # Mock configuration
        mock_cfg = MagicMock()

        # Mock validation
        mock_global_config = MagicMock()
        mock_validate.return_value = mock_global_config

        # Mock scheduler
        mock_scheduler = MagicMock()
        mock_schedule_domains.return_value = mock_scheduler

        # Call scheduler main
        scheduler_main(mock_cfg)

        # Verify calls
        mock_validate.assert_called_once_with(mock_cfg)
        mock_configure_logging.assert_called_once_with(mock_global_config.logging)
        mock_schedule_domains.assert_called_once_with(mock_global_config)
        mock_scheduler.start.assert_called_once()
        mock_logger.info.assert_called_with("Scheduler is running. Press Ctrl+C to exit.")

    @patch("insert_package_name.scheduler_main.load_and_validate_config")
    @patch("insert_package_name.scheduler_main.configure_logging")
    @patch("insert_package_name.scheduler_main.schedule_domains")
    @patch("insert_package_name.scheduler_main.get_logger")
    def test_scheduler_main_keyboard_interrupt(
        self, mock_get_logger, mock_schedule_domains, mock_configure_logging, mock_validate
    ):
        """Test scheduler main with keyboard interrupt."""
        # Mock configuration
        mock_cfg = MagicMock()

        # Mock validation
        mock_global_config = MagicMock()
        mock_validate.return_value = mock_global_config

        # Mock scheduler that raises KeyboardInterrupt
        mock_scheduler = MagicMock()
        mock_scheduler.start.side_effect = KeyboardInterrupt()
        mock_schedule_domains.return_value = mock_scheduler

        # Mock logger
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger

        # Call scheduler main - should handle KeyboardInterrupt gracefully
        scheduler_main(mock_cfg)

        # Verify scheduler was started
        mock_scheduler.start.assert_called_once()

    @patch("insert_package_name.scheduler_main.load_and_validate_config")
    def test_scheduler_main_validation_error(self, mock_validate):
        """Test scheduler main with validation error."""
        # Mock validation to raise an exception
        mock_validate.side_effect = ValueError("Invalid configuration")

        mock_cfg = MagicMock()

        # Should raise the validation error
        with pytest.raises(ValueError, match="Invalid configuration"):
            scheduler_main(mock_cfg)

    @patch("insert_package_name.scheduler_main.load_and_validate_config")
    @patch("insert_package_name.scheduler_main.configure_logging")
    @patch("insert_package_name.scheduler_main.schedule_domains")
    def test_scheduler_main_scheduler_error(self, mock_schedule_domains, mock_configure_logging, mock_validate):
        """Test scheduler main with scheduler creation error."""
        # Mock configuration
        mock_cfg = MagicMock()

        # Mock validation
        mock_global_config = MagicMock()
        mock_validate.return_value = mock_global_config

        # Mock scheduler creation to raise an exception
        mock_schedule_domains.side_effect = ValueError("No domains scheduled")

        # Should raise the scheduler error
        with pytest.raises(ValueError, match="No domains scheduled"):
            scheduler_main(mock_cfg)
