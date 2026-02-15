"""Integration tests for API functionality."""

from __future__ import annotations

from insert_package_name.api import DataFlow, list_domains, validate_config


class TestAPIIntegration:
    """Integration tests for API functionality."""

    def test_dataflow_integration(self):
        """Test DataFlow class integration."""
        df = DataFlow()

        # Test basic functionality
        domains = df.domains()
        assert isinstance(domains, list)
        assert len(domains) > 0

        # Test method chaining
        result = df.with_domains(domains[:1])
        assert result is df

        # Test config retrieval
        config = df.get_config()
        assert isinstance(config, dict)
        assert "domains" in config

        # Test validation
        is_valid = df.validate()
        assert isinstance(is_valid, bool)

    def test_convenience_functions_integration(self):
        """Test convenience functions integration."""
        # Test list_domains
        domains = list_domains()
        assert isinstance(domains, list)
        assert len(domains) > 0

        # Test validate_config
        is_valid = validate_config()
        assert isinstance(is_valid, bool)
        assert is_valid is True

    def test_dataflow_method_chaining(self):
        """Test DataFlow method chaining works correctly."""
        df = DataFlow()

        # Chain multiple methods
        result = df.with_domains(["example_domain"]).with_config_overrides({"test": "value"})

        assert result is df
        assert df._domains == ["example_domain"]
        assert hasattr(df, "_overrides")
        assert df._overrides == {"test": "value"}

    def test_dataflow_config_path(self, tmp_path):
        """Test DataFlow with custom config path."""
        df = DataFlow(tmp_path)
        assert df.config_path == tmp_path

        config = df.get_config()
        assert "config_path" in config
