"""Web GUI for data pipeline configuration and execution."""

from __future__ import annotations

import subprocess
import sys
import threading
import time
from pathlib import Path
from typing import Any

from flask import Flask, jsonify, render_template, request
from flask_cors import CORS

from insert_package_name.api import DataFlow, list_domains
from insert_package_name.main import get_config_directory


class PipelineRunner:
    """Manages pipeline execution in background threads."""

    def __init__(self) -> None:
        self.running_processes: dict[str, subprocess.Popen[str]] = {}
        self.run_logs: dict[str, list[str]] = {}
        self.run_status: dict[str, str] = {}

    def start_run(self, run_id: str, domains: list[str] | None = None) -> bool:
        """Start a pipeline run in background."""
        try:
            cmd = [sys.executable, "-m", "insert_package_name.main"]
            if domains:
                # Use Hydra's list syntax: run_domains=[domain1,domain2]
                domains_str = ",".join(f'"{d}"' for d in domains)
                cmd.append(f"run_domains=[{domains_str}]")

            # Start process
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, cwd=Path.cwd())

            self.running_processes[run_id] = process
            self.run_logs[run_id] = []
            self.run_status[run_id] = "running"

            # Start log monitoring thread
            threading.Thread(target=self._monitor_process, args=(run_id, process), daemon=True).start()

            return True
        except Exception as e:
            self.run_status[run_id] = f"error: {e}"
            return False

    def _monitor_process(self, run_id: str, process: subprocess.Popen[str]) -> None:
        """Monitor process output and update logs."""
        try:
            while True:
                if process.poll() is not None:
                    # Process finished
                    break

                # Read output
                if process.stdout:
                    line = process.stdout.readline()
                    if line:
                        self.run_logs[run_id].append(line.strip())

                time.sleep(0.1)

            # Get final output
            if process.stdout:
                remaining = process.stdout.read()
                if remaining:
                    self.run_logs[run_id].extend(remaining.strip().split("\n"))

            # Update status
            return_code = process.returncode
            if return_code == 0:
                self.run_status[run_id] = "completed"
            else:
                self.run_status[run_id] = f"failed (exit code {return_code})"

        except Exception as e:
            self.run_status[run_id] = f"error: {e}"
        finally:
            # Clean up
            if run_id in self.running_processes:
                del self.running_processes[run_id]

    def stop_run(self, run_id: str) -> bool:
        """Stop a running pipeline."""
        if run_id in self.running_processes:
            process = self.running_processes[run_id]
            process.terminate()
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                process.kill()
            return True
        return False

    def get_run_status(self, run_id: str) -> dict[str, Any]:
        """Get status of a run."""
        return {
            "status": self.run_status.get(run_id, "unknown"),
            "logs": self.run_logs.get(run_id, []),
            "is_running": run_id in self.running_processes,
        }


# Global runner instance
runner = PipelineRunner()

# Flask app
app = Flask(__name__, template_folder=str(Path(__file__).parent / "templates"))
CORS(app)


@app.route("/")
def index():
    """Main dashboard page."""
    return render_template("index.html")


@app.route("/api/domains")
def get_domains():
    """Get list of available domains."""
    try:
        domains = list_domains()
        return jsonify({"domains": domains})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/config")
def get_config():
    """Get current configuration."""
    try:
        config_path = get_config_directory()
        return jsonify(
            {
                "config_path": config_path,
                "environment": "dev",  # Could be made configurable
            }
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/run", methods=["POST"])
def start_run():
    """Start a pipeline run."""
    try:
        data = request.get_json()
        domains = data.get("domains", [])
        run_id = f"run_{int(time.time())}"

        success = runner.start_run(run_id, domains if domains else None)

        if success:
            return jsonify({"run_id": run_id, "status": "started"})
        else:
            return jsonify({"error": "Failed to start run"}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/run/<run_id>/status")
def get_run_status(run_id: str):
    """Get status of a specific run."""
    try:
        status = runner.get_run_status(run_id)
        return jsonify(status)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/run/<run_id>/stop", methods=["POST"])
def stop_run(run_id: str):
    """Stop a running pipeline."""
    try:
        success = runner.stop_run(run_id)
        return jsonify({"stopped": success})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/validate")
def validate_config():
    """Validate current configuration."""
    try:
        df = DataFlow()
        is_valid = df.validate()
        return jsonify({"valid": is_valid})
    except Exception as e:
        return jsonify({"valid": False, "error": str(e)})


def create_app() -> Flask:
    """Create and configure the Flask application."""
    return app


def run_gui(host: str = "127.0.0.1", port: int = 5000, debug: bool = False) -> None:
    """Run the GUI web application."""
    app.run(host=host, port=port, debug=debug)


if __name__ == "__main__":
    run_gui(debug=True)
