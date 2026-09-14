from __future__ import annotations

from marrowai.model_manager import OfflineModelManager
from marrowai.scaffold import ProjectScaffold


def test_offline_model_manager_handles_unavailable_runtime():
    manager = OfflineModelManager(base_url="http://127.0.0.1:1")
    assert manager.is_available() is False
    assert manager.ensure_model("llama3.2") is False


def test_model_download_reports_configured_endpoint_problem():
    manager = OfflineModelManager(base_url="http://127.0.0.1:1")

    success, message = manager.download_model("mistral")

    assert success is False
    assert "not reachable" in message


def test_project_scaffold_creates_backend_project(tmp_path):
    scaffold = ProjectScaffold(base_dir=str(tmp_path))
    created = scaffold.create_backend_project("demoapi")

    assert created is True
    assert (tmp_path / "demoapi" / "README.md").exists()
    assert (tmp_path / "demoapi" / "app.py").exists()
