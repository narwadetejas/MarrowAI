from __future__ import annotations

import io
from unittest.mock import MagicMock
from marrowai.web_gui import MarrowWebHandler


def test_web_handler_serves_html():
    handler = MarrowWebHandler.__new__(MarrowWebHandler)
    handler.path = "/"
    handler.headers = {}
    handler.rfile = io.BytesIO()
    handler.wfile = io.BytesIO()

    handler.send_response = MagicMock()
    handler.send_header = MagicMock()
    handler.end_headers = MagicMock()

    handler.do_GET()

    handler.send_response.assert_called_with(200)
    output = handler.wfile.getvalue().decode("utf-8")
    assert "<title>MarrowAI — Autonomous Linux Operating Assistant</title>" in output
    assert "Offline Model Manager" in output


def test_web_handler_serves_status_api():
    handler = MarrowWebHandler.__new__(MarrowWebHandler)
    handler.path = "/api/status"
    handler.headers = {}
    handler.rfile = io.BytesIO()
    handler.wfile = io.BytesIO()

    handler.send_response = MagicMock()
    handler.send_header = MagicMock()
    handler.end_headers = MagicMock()

    handler.do_GET()

    handler.send_response.assert_called_with(200)
    output = handler.wfile.getvalue().decode("utf-8")
    assert "cpu_load" in output
    assert "ram_free_mb" in output


def test_web_handler_serves_tts_api():
    handler = MarrowWebHandler.__new__(MarrowWebHandler)
    handler.path = "/api/tts?voice=indian_female&text=Hello"
    handler.headers = {}
    handler.rfile = io.BytesIO()
    handler.wfile = io.BytesIO()
    handler.voice_engine = MagicMock()
    handler.voice_engine.synthesize_neural_audio.return_value = b"ID3\x04\x00\x00fake-mp3-audio"

    handler.send_response = MagicMock()
    handler.send_header = MagicMock()
    handler.end_headers = MagicMock()

    handler.do_GET()

    handler.send_response.assert_called_with(200)
    handler.send_header.assert_any_call("Content-Type", "audio/mpeg")
    assert handler.wfile.getvalue() == b"ID3\x04\x00\x00fake-mp3-audio"


def test_web_handler_serves_tts_wav_fallback():
    handler = MarrowWebHandler.__new__(MarrowWebHandler)
    handler.path = "/api/tts?voice=indian_female&text=Hello+Offline"
    handler.headers = {}
    handler.rfile = io.BytesIO()
    handler.wfile = io.BytesIO()
    handler.voice_engine = MagicMock()
    handler.voice_engine.synthesize_neural_audio.return_value = None
    handler.voice_engine.synthesize_offline_wav.return_value = b"RIFF\x24\x00\x00\x00WAVEfmt fake-wav"

    handler.send_response = MagicMock()
    handler.send_header = MagicMock()
    handler.end_headers = MagicMock()

    handler.do_GET()

    handler.send_response.assert_called_with(200)
    handler.send_header.assert_any_call("Content-Type", "audio/wav")
    assert handler.wfile.getvalue() == b"RIFF\x24\x00\x00\x00WAVEfmt fake-wav"


def test_web_handler_serves_models_api():
    handler = MarrowWebHandler.__new__(MarrowWebHandler)
    handler.path = "/api/models"
    handler.headers = {}
    handler.rfile = io.BytesIO()
    handler.wfile = io.BytesIO()
    handler.model_manager = MagicMock()
    handler.model_manager.list_local_models_detailed.return_value = [
        {"name": "qwen2.5-coder:14b", "size_formatted": "8.4 GB"}
    ]
    handler.model_manager.is_available.return_value = True

    handler.send_response = MagicMock()
    handler.send_header = MagicMock()
    handler.end_headers = MagicMock()

    handler.do_GET()

    handler.send_response.assert_called_with(200)
    output = handler.wfile.getvalue().decode("utf-8")
    assert "qwen2.5-coder:14b" in output
    assert "8.4 GB" in output


def test_web_handler_sets_active_model():
    handler = MarrowWebHandler.__new__(MarrowWebHandler)
    handler.path = "/api/models/active"
    body = b'{"model": "qwen2.5-coder:14b"}'
    handler.headers = {"Content-Length": str(len(body))}
    handler.rfile = io.BytesIO(body)
    handler.wfile = io.BytesIO()
    handler.assistant = MagicMock()

    handler.send_response = MagicMock()
    handler.send_header = MagicMock()
    handler.end_headers = MagicMock()

    handler.do_POST()

    handler.send_response.assert_called_with(200)
    output = handler.wfile.getvalue().decode("utf-8")
    assert '"success": true' in output
    assert "qwen2.5-coder:14b" in output



