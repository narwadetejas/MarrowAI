from __future__ import annotations

from .diagnostics import CapabilityDetector


def main() -> None:
    report = CapabilityDetector().detect()
    print(f"Platform: {report.platform}")
    print(f"Python: {report.python_version}")
    print(f"CPU: {report.cpu}")
    print(f"Ollama: {'yes' if report.has_ollama else 'no'}")
    print(f"Git: {'yes' if report.has_git else 'no'}")
    print(f"FFmpeg: {'yes' if report.has_ffmpeg else 'no'}")
    print(f"PulseAudio: {'yes' if report.has_pulseaudio else 'no'}")
    print(f"Wayland: {'yes' if report.has_wayland else 'no'}")
    print("Support summary:")
    for key, value in report.support_summary.items():
        print(f"  - {key}: {value}")


if __name__ == "__main__":
    main()
