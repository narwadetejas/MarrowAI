from __future__ import annotations

from marrowai.voice import OfflineSTTProvider, OfflineTTSProvider, STTProvider, TTSProvider


def test_voice_provider_interfaces_are_defined():
    assert issubclass(STTProvider, object)
    assert issubclass(TTSProvider, object)


def test_offline_stt_provider_normalizes_text():
    provider = OfflineSTTProvider()
    transcript = provider.transcribe(b"voice sample")

    assert transcript == "voice sample"


def test_offline_tts_provider_returns_text_for_speech():
    provider = OfflineTTSProvider()
    result = provider.speak("hello from marrowai")

    assert result == "hello from marrowai"
