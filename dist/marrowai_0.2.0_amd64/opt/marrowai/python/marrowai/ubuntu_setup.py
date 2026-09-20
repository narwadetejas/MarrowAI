from __future__ import annotations

import shutil
from pathlib import Path


class UbuntuSetupAssistant:
    """Creates an offline Linux setup script for MarrowAI prerequisites."""

    def __init__(self, target_dir: str | None = None) -> None:
        self.target_dir = Path(target_dir or ".")

    def generate_setup_script(self, path: str | None = None) -> Path:
        script_path = Path(path or self.target_dir / "install_marrowai_ubuntu.sh")
        script_path.parent.mkdir(parents=True, exist_ok=True)
        script_path.write_text(
            "#!/usr/bin/env bash\n"
            "set -e\n"
            "sudo apt-get update\n"
            "sudo apt-get install -y python3 python3-venv python3-pip ffmpeg espeak-ng git curl\n"
            "curl -fsSL https://ollama.com/install.sh | sh\n"
            "echo 'MarrowAI dependencies installed.'\n",
            encoding="utf-8",
        )
        script_path.chmod(0o755)
        return script_path

    def ensure_runtime(self) -> dict[str, bool]:
        return {
            "python": shutil.which("python3") is not None,
            "git": shutil.which("git") is not None,
            "ffmpeg": shutil.which("ffmpeg") is not None,
            "espeak": shutil.which("espeak-ng") is not None or shutil.which("espeak") is not None,
            "ollama": shutil.which("ollama") is not None,
        }


def main() -> None:
    assistant = UbuntuSetupAssistant()
    path = assistant.generate_setup_script("install_marrowai_ubuntu.sh")
    print(f"Setup script created at {path}")
    print(assistant.ensure_runtime())


if __name__ == "__main__":
    main()
