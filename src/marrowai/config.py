from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass
class AppConfig:
    model_provider: str = "ollama"
    model_name: str = "llama3.2"
    ollama_base_url: str = "http://127.0.0.1:11434"
    voice_enabled: bool = True
    voice_profile: str = "indian_female"  # options: "indian_female", "indian_male"
    voice_speed: int = 150
    voice_pitch: int = 55
    interactive_mode: bool = True


def get_config() -> AppConfig:
    return AppConfig(
        model_provider=os.getenv("MARROWAI_MODEL_PROVIDER", "ollama"),
        model_name=os.getenv("MARROWAI_MODEL_NAME", "llama3.2"),
        ollama_base_url=os.getenv("MARROWAI_OLLAMA_BASE_URL", "http://127.0.0.1:11434"),
        voice_enabled=os.getenv("MARROWAI_VOICE_ENABLED", "1") not in {"0", "false", "False"},
        voice_profile=os.getenv("MARROWAI_VOICE_PROFILE", "indian_female"),
        voice_speed=int(os.getenv("MARROWAI_VOICE_SPEED", "150")),
        voice_pitch=int(os.getenv("MARROWAI_VOICE_PITCH", "55")),
        interactive_mode=os.getenv("MARROWAI_INTERACTIVE_MODE", "1") not in {"0", "false", "False"},
    )
