from __future__ import annotations

import platform
import shutil
import sys
from dataclasses import dataclass


@dataclass
class CapabilityReport:
    platform: str
    python_version: str
    cpu: str
    has_ollama: bool
    has_git: bool
    has_ffmpeg: bool
    has_pulseaudio: bool
    has_wayland: bool
    support_summary: dict[str, str]


class CapabilityDetector:
    def detect(self) -> CapabilityReport:
        system = platform.system()
        cpu = platform.machine() or "unknown"
        has_ollama = shutil.which("ollama") is not None
        has_git = shutil.which("git") is not None
        has_ffmpeg = shutil.which("ffmpeg") is not None
        has_pulseaudio = shutil.which("pulseaudio") is not None
        has_wayland = "WAYLAND_DISPLAY" in __import__("os").environ

        return CapabilityReport(
            platform=system,
            python_version=sys.version.split()[0],
            cpu=cpu,
            has_ollama=has_ollama,
            has_git=has_git,
            has_ffmpeg=has_ffmpeg,
            has_pulseaudio=has_pulseaudio,
            has_wayland=has_wayland,
            support_summary={
                "offline_model_runtime": "ollama" if has_ollama else "not detected",
                "version_control": "git" if has_git else "not detected",
                "audio_pipeline": "ffmpeg" if has_ffmpeg else "not detected",
                "desktop_session": "wayland" if has_wayland else "x11 or tty",
            },
        )
