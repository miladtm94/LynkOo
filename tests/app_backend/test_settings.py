import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from app.backend.api import routes_settings
from app.backend.main import create_app
from app.backend.models.settings import AppSettings
from app.backend.services.download_manager import DownloadManager


def test_settings_normalize_output_directory():
    settings = AppSettings(output_directory="~/Downloads/Xpotify")
    assert str(settings.output_directory).endswith("Downloads/Xpotify")


def test_settings_reject_unsupported_audio_format():
    with pytest.raises(ValidationError):
        AppSettings(default_audio_format="exe")


def test_update_settings_creates_selected_output_directory(tmp_path):
    selected = tmp_path / "selected" / "downloads"
    manager = DownloadManager(settings=AppSettings(output_directory=tmp_path), providers=[])
    client = TestClient(create_app(manager=manager))

    response = client.put("/api/settings", json={"output_directory": str(selected)})

    assert response.status_code == 200
    assert selected.is_dir()
    assert response.json()["settings"]["output_directory"] == str(selected)


def test_update_settings_rejects_output_file_path(tmp_path):
    selected = tmp_path / "not-a-folder"
    selected.write_text("nope")
    manager = DownloadManager(settings=AppSettings(output_directory=tmp_path), providers=[])
    client = TestClient(create_app(manager=manager))

    response = client.put("/api/settings", json={"output_directory": str(selected)})

    assert response.status_code == 400
    assert "not a folder" in response.json()["detail"]


def test_macos_folder_picker_uses_osascript(monkeypatch):
    class CompletedProcess:
        returncode = 0
        stdout = "/tmp/Xpotify\n"
        stderr = ""

    def fake_run(args, capture_output, text, check):
        assert args[0] == "osascript"
        assert capture_output is True
        assert text is True
        assert check is False
        return CompletedProcess()

    monkeypatch.setattr(routes_settings.sys, "platform", "darwin")
    monkeypatch.setattr(routes_settings.subprocess, "run", fake_run)

    response = routes_settings._select_output_directory_sync()

    assert response.selected is True
    assert response.path is not None
    assert str(response.path) == "/tmp/Xpotify"
    assert response.message == "Output folder selected."


def test_macos_folder_picker_reports_cancel(monkeypatch):
    class CompletedProcess:
        returncode = 1
        stdout = ""
        stderr = "execution error: User canceled. (-128)"

    monkeypatch.setattr(routes_settings.sys, "platform", "darwin")
    monkeypatch.setattr(
        routes_settings.subprocess,
        "run",
        lambda *args, **kwargs: CompletedProcess(),
    )

    response = routes_settings._select_output_directory_sync()

    assert response.selected is False
    assert response.message == "Folder selection was cancelled."
