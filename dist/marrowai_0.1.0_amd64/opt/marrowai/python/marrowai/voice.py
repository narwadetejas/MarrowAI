from __future__ import annotations

from abc import ABC, abstractmethod


class STTProvider(ABC):
    @abstractmethod
    def transcribe(self, audio_bytes: bytes) -> str:
        raise NotImplementedError


class TTSProvider(ABC):
    @abstractmethod
    def speak(self, text: str) -> str:
        raise NotImplementedError


class OfflineSTTProvider(STTProvider):
    def transcribe(self, audio_bytes: bytes) -> str:
        return audio_bytes.decode("utf-8", errors="ignore").strip()


class OfflineTTSProvider(TTSProvider):
    def speak(self, text: str) -> str:
        return text
