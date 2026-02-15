"""Tests for the programmatic API."""

from __future__ import annotations

import sys
from unittest.mock import patch

from insert_package_name.api import DataFlow, list_domains, run_domains, validate_config


class TestDataFlow:
    """Test the DataFlow class."""

    def test_dataflow_init(self):
        """Test DataFlow initialization."""
        df = DataFlow()
        assert df.config_path is None
        assert df._domains is None

    def test_dataflow_init_with_path(self, tmp_path):
        """Test DataFlow initialization with config path."""
        df = DataFlow(tmp_path)
        assert df.config_path == tmp_path

    def test_dataflow_domains(self):
        """Test getting domains list."""
        df = DataFlow()
        domains = df.domains()
        assert isinstance(domains, list)
        assert "example_domain" in domains

    def test_dataflow_with_domains(self):
        """Test with_domains method."""
        df = DataFlow()
        result = df.with_domains(["domain1", "domain2"])
        assert result is df  # Method chaining
        assert df._domains == ["domain1", "domain2"]

    def test_dataflow_with_config_overrides(self):
        """Test with_config_overrides method."""
        df = DataFlow()
        overrides = {"param": "value"}
        result = df.with_config_overrides(overrides)
        assert result is df  # Method chaining
        assert hasattr(df, "_overrides")
        assert df._overrides == overrides

    @patch("subprocess.run")
    def test_dataflow_run(self, mock_subprocess):
        """Test DataFlow run method."""
        mock_subprocess.return_value.returncode = 0

        df = DataFlow()
        df.run()

        mock_subprocess.assert_called_once()
        args, kwargs = mock_subprocess.call_args
        assert args[0][0] == sys.executable  # sys.executable
        assert "-m" in args[0]
        assert "insert_package_name.main" in args[0]

    @patch("subprocess.run")
    def test_dataflow_run_with_domains(self, mock_subprocess):
        """Test DataFlow run method with specific domains."""
        mock_subprocess.return_value.returncode = 0

        df = DataFlow()
        df.with_domains(["domain1"]).run(["domain2"])

        # Should use the domains passed to run(), not with_domains()
        mock_subprocess.assert_called_once()

    def test_dataflow_validate(self):
        """Test DataFlow validate method."""
        df = DataFlow()
        result = df.validate()
        assert isinstance(result, bool)
        assert result is True  # Should validate successfully

    def test_dataflow_get_config(self):
        """Test DataFlow get_config method."""
        df = DataFlow()
        config = df.get_config()
        assert isinstance(config, dict)
        assert "domains" in config
        assert "example_domain" in config["domains"]


class TestConvenienceFunctions:
    """Test convenience functions."""

    @patch("subprocess.run")
    def test_run_domains(self, mock_subprocess):
        """Test run_domains convenience function."""
        mock_subprocess.return_value.returncode = 0

        run_domains()

        mock_subprocess.assert_called_once()

    def test_list_domains(self):
        """Test list_domains convenience function."""
        domains = list_domains()
        assert isinstance(domains, list)
        assert "example_domain" in domains

    def test_validate_config(self):
        """Test validate_config convenience function."""
        result = validate_config()
        assert isinstance(result, bool)
        assert result is True

    @patch("subprocess.run")
    def test_run_domains_with_specific_domains(self, mock_subprocess):
        """Test run_domains with specific domains."""
        mock_subprocess.return_value.returncode = 0

        run_domains(["domain1", "domain2"])

        mock_subprocess.assert_called_once()

    def test_list_domains_with_config_path(self, tmp_path):
        """Test list_domains with config path."""
        domains = list_domains(tmp_path)
        assert isinstance(domains, list)

    def test_validate_config_with_config_path(self, tmp_path):
        """Test validate_config with config path."""
        result = validate_config(tmp_path)
        assert isinstance(result, bool)
