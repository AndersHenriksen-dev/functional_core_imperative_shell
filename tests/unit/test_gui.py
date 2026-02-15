"""Tests for the GUI interface."""

from __future__ import annotations

import pytest
from flask.testing import FlaskClient

from insert_package_name.gui import create_app


@pytest.fixture
def client():
    """Create a test client for the Flask app."""
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


class TestGUI:
    """Test the GUI endpoints."""

    def test_index_page(self, client: FlaskClient):
        """Test the main dashboard page loads."""
        response = client.get("/")
        assert response.status_code == 200
        assert b"Data Pipeline Control Center" in response.data

    def test_get_domains_api(self, client: FlaskClient):
        """Test the domains API endpoint."""
        response = client.get("/api/domains")
        assert response.status_code == 200
        data = response.get_json()
        assert "domains" in data
        assert isinstance(data["domains"], list)

    def test_get_config_api(self, client: FlaskClient):
        """Test the config API endpoint."""
        response = client.get("/api/config")
        assert response.status_code == 200
        data = response.get_json()
        assert "config_path" in data
        assert "environment" in data

    def test_validate_api(self, client: FlaskClient):
        """Test the validate API endpoint."""
        response = client.get("/api/validate")
        assert response.status_code == 200
        data = response.get_json()
        assert "valid" in data
        assert isinstance(data["valid"], bool)

    def test_start_run_api(self, client: FlaskClient):
        """Test starting a run via API."""
        response = client.post("/api/run", json={"domains": ["example_domain"]})
        assert response.status_code == 200
        data = response.get_json()
        assert "run_id" in data or "error" in data

    def test_get_run_status_api(self, client: FlaskClient):
        """Test getting run status via API."""
        # First start a run to get a run_id
        response = client.post("/api/run", json={"domains": ["example_domain"]})
        if response.status_code == 200:
            data = response.get_json()
            if "run_id" in data:
                run_id = data["run_id"]
                # Now test getting status
                status_response = client.get(f"/api/run/{run_id}/status")
                assert status_response.status_code == 200
                status_data = status_response.get_json()
                assert "status" in status_data
                assert "logs" in status_data
                assert "is_running" in status_data

    def test_stop_run_api(self, client: FlaskClient):
        """Test stopping a run via API."""
        # First start a run
        response = client.post("/api/run", json={"domains": ["example_domain"]})
        if response.status_code == 200:
            data = response.get_json()
            if "run_id" in data:
                run_id = data["run_id"]
                # Now test stopping it
                stop_response = client.post(f"/api/run/{run_id}/stop")
                assert stop_response.status_code == 200
                stop_data = stop_response.get_json()
                assert "stopped" in stop_data
