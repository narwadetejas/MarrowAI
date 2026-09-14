from __future__ import annotations

from marrowai.voice_engine import OfflineVoiceEngine
from marrowai.ubuntu_setup import UbuntuSetupAssistant


def test_voice_engine_reports_status():
    engine = OfflineVoiceEngine()
    status = engine.status()

    assert "tts_backend" in status
    assert "stt_backend" in status


def test_voice_engine_handles_text_and_audio_fallback():
    engine = OfflineVoiceEngine()
    speech = engine.speak("hello from marrowai")
    audio = engine.transcribe(source_text="hello from marrowai")

    assert speech.ok or speech.engine == "fallback"
    assert audio.ok is True


def test_ubuntu_setup_script_is_generated():
    assistant = UbuntuSetupAssistant(target_dir=".")
    path = assistant.generate_setup_script("setup_marrowai.sh")

    assert path.exists()
    assert "ollama" in path.read_text(encoding="utf-8")
