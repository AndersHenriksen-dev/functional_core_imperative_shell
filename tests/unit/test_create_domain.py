"""Tests for domain creation functionality."""

from __future__ import annotations

import pytest

from insert_package_name.create_domain import (
    create_domain_config,
    create_domain_impl,
    create_domain_template,
)


class TestDomainCreation:
    """Test domain creation functionality."""

    def test_create_domain_template(self, tmp_path):
        """Test creating domain template files."""
        create_domain_template("test_domain", tmp_path)

        domain_dir = tmp_path / "domains" / "test_domain"
        assert domain_dir.exists()

        # Check all required files exist
        assert (domain_dir / "__init__.py").exists()
        assert (domain_dir / "ops.py").exists()
        assert (domain_dir / "pipeline.py").exists()
        assert (domain_dir / "schemas.py").exists()

        # Check content of ops.py
        ops_content = (domain_dir / "ops.py").read_text()
        assert "test_domain domain" in ops_content
        assert "compute_scores" in ops_content
        assert "compute_metrics" in ops_content

        # Check content of pipeline.py
        pipeline_content = (domain_dir / "pipeline.py").read_text()
        assert "test_domain domain" in pipeline_content
        assert "run(cfg: DomainConfig)" in pipeline_content

        # Check content of schemas.py
        schemas_content = (domain_dir / "schemas.py").read_text()
        assert "GoldScoresSchema" in schemas_content
        assert "GoldMetricsSchema" in schemas_content

    def test_create_domain_config(self, tmp_path):
        """Test creating domain configuration."""
        config_dir = tmp_path / "configs"
        create_domain_config("test_domain", config_dir)

        config_file = config_dir / "domains" / "test_domain.yaml"
        assert config_file.exists()

        content = config_file.read_text()
        assert "test_domain:" in content
        assert 'name: "Test Domain"' in content
        assert "enabled: true" in content
        assert 'tags: ["daily"]' in content

    def test_create_domain_impl(self, tmp_path, capsys):
        """Test the complete domain creation implementation."""
        config_dir = tmp_path / "configs"

        create_domain_impl("test_domain", str(tmp_path), str(config_dir))

        captured = capsys.readouterr()
        assert "Creating domain 'test_domain'..." in captured.out
        assert "[OK] Created domain code" in captured.out
        assert "[OK] Created domain config" in captured.out
        assert "Next steps:" in captured.out

        # Check files were created
        domain_dir = tmp_path / "domains" / "test_domain"
        assert domain_dir.exists()
        assert (domain_dir / "ops.py").exists()

        config_file = config_dir / "domains" / "test_domain.yaml"
        assert config_file.exists()

    def test_create_domain_invalid_name(self, tmp_path):
        """Test creating domain with invalid name."""
        with pytest.raises(ValueError, match="Domain name must contain only"):
            create_domain_impl("test-domain", str(tmp_path), str(tmp_path))

    def test_create_domain_template_overwrite(self, tmp_path):
        """Test that domain template creation handles existing directories."""
        # Create domain twice
        create_domain_template("test_domain", tmp_path)
        create_domain_template("test_domain", tmp_path)  # Should not fail

        domain_dir = tmp_path / "domains" / "test_domain"
        assert domain_dir.exists()
        assert (domain_dir / "ops.py").exists()
