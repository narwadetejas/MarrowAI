from __future__ import annotations

import json
from unittest.mock import MagicMock, patch
from marrowai.model_manager import OfflineModelManager


def test_download_model_streams_progress_and_percentages():
    manager = OfflineModelManager(base_url="http://127.0.0.1:11434")

    # Mock streaming response lines from Ollama /api/pull
    mock_events = [
        json.dumps({"status": "pulling manifest"}),
        json.dumps({"status": "downloading", "total": 1000, "completed": 250}),
        json.dumps({"status": "downloading", "total": 1000, "completed": 500}),
        json.dumps({"status": "downloading", "total": 1000, "completed": 750}),
        json.dumps({"status": "verifying sha256 digest"}),
        json.dumps({"status": "writing manifest"}),
        json.dumps({"status": "success"}),
    ]
    raw_lines = [f"{e}\n".encode("utf-8") for e in mock_events]

    mock_resp = MagicMock()
    mock_resp.__enter__.return_value = raw_lines

    recorded_pcts = []
    recorded_details = []

    def on_progress(pct: float, detail: str, comp: int, tot: int) -> None:
        recorded_pcts.append(pct)
        recorded_details.append(detail)

    with patch("marrowai.model_manager.OfflineModelManager.start_service", return_value=(True, "Ready")):
        with patch("urllib.request.urlopen", return_value=mock_resp):
            ok, msg = manager.download_model("test-model", progress_callback=on_progress, voice_notify=False)

    assert ok is True
    assert "test-model" in msg
    assert len(recorded_pcts) > 0
    # Check that percentage progressed correctly
    assert 25.0 in recorded_pcts
    assert 50.0 in recorded_pcts
    assert 75.0 in recorded_pcts
    assert 100.0 in recorded_pcts
    assert any("25.0%" in d for d in recorded_details)
    assert any("50.0%" in d for d in recorded_details)
