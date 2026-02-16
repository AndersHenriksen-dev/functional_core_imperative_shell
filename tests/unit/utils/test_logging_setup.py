"""Tests for logging utilities."""

from __future__ import annotations

import logging
import os
import tempfile
from unittest.mock import MagicMock, patch

import pytest

from insert_package_name.utils.logging import (
    _format_elapsed_time,
    _raise_custom_exception,
    get_logger,
    log_function_execution,
    setup_logging,
)


class TestSetupLogging:
    """Test setup_logging function."""

    def test_setup_logging_basic(self):
        """Test basic logging setup."""
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch("sys.argv", ["test_script.py"]):
                setup_logging(temp_dir)

            # Check that log directory was created
            log_dir = os.path.join(temp_dir, "logs")
            assert os.path.exists(log_dir)
            assert os.path.isdir(log_dir)

            # Shutdown logging to release file handles
            logging.shutdown()

    def test_setup_logging_creates_log_file(self):
        """Test that log file is created."""
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch("sys.argv", ["test_script.py"]):
                setup_logging(temp_dir)

            log_dir = os.path.join(temp_dir, "logs")
            # Should have created a log file
            log_files = [f for f in os.listdir(log_dir) if f.endswith(".log")]
            assert len(log_files) == 1
            assert log_files[0].startswith("TEST_SCRIPT_")

            # Shutdown logging to release file handles
            logging.shutdown()


class TestGetLogger:
    """Test get_logger function."""

    def test_get_logger_basic(self):
        """Test basic logger retrieval."""
        logger = get_logger("test_module")

        assert isinstance(logger, logging.Logger)
        assert logger.name == "test_module"

    def test_get_logger_same_instance(self):
        """Test that same logger instance is returned for same name."""
        logger1 = get_logger("test_module")
        logger2 = get_logger("test_module")

        assert logger1 is logger2

    def test_get_logger_different_names(self):
        """Test that different loggers are returned for different names."""
        logger1 = get_logger("module1")
        logger2 = get_logger("module2")

        assert logger1 is not logger2
        assert logger1.name == "module1"
        assert logger2.name == "module2"


class TestLogFunctionExecution:
    """Test log_function_execution decorator."""

    def test_log_function_execution_success(self):
        """Test successful function execution logging."""

        @log_function_execution
        def test_function(x, y=10):
            return x + y

        with patch("logging.getLogger") as mock_get_logger:
            mock_logger = MagicMock()
            mock_get_logger.return_value = mock_logger

            result = test_function(5, y=15)

        assert result == 20
        # Should log start and finish
        assert mock_logger.info.call_count == 2
        assert mock_logger.debug.call_count == 1

    def test_log_function_execution_with_exception(self):
        """Test function execution logging with exception."""

        @log_function_execution
        def failing_function():
            raise ValueError("test error")

        with patch("logging.getLogger") as mock_get_logger:
            mock_logger = MagicMock()
            mock_get_logger.return_value = mock_logger

            with pytest.raises(ValueError):
                failing_function()

        # Should log start and error
        assert mock_logger.info.call_count == 1
        assert mock_logger.error.call_count == 1


class TestFormatElapsedTime:
    """Test _format_elapsed_time function."""

    def test_format_elapsed_time_seconds(self):
        """Test formatting time in seconds."""
        result = _format_elapsed_time(0, 30.5)
        assert result == "30.50 seconds"

    def test_format_elapsed_time_minutes(self):
        """Test formatting time in minutes and seconds."""
        result = _format_elapsed_time(0, 90.5)
        assert "1 minutes and 30.50 seconds" in result


class TestRaiseCustomException:
    """Test _raise_custom_exception function."""

    def test_raise_custom_exception(self):
        """Test that custom exception is raised."""
        original_exception = ValueError("original error")

        with pytest.raises(ValueError) as exc_info:
            _raise_custom_exception(original_exception, "test_function")

        # Should re-raise the same exception
        assert exc_info.value == original_exception
