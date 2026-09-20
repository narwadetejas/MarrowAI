from __future__ import annotations

import tkinter as tk
from unittest.mock import MagicMock
from marrowai.gui import MarrowAIWindow, MODEL_CATALOG, THEME


def test_gui_constants():
    assert "llama3.2" in MODEL_CATALOG
    assert "deepseek-r1:7b" in MODEL_CATALOG
    assert "bg_dark" in THEME
    assert "accent_cyan" in THEME
    assert "status_green" in THEME


def test_gui_window_construction():
    try:
        root = tk.Tk()
        root.withdraw()
    except tk.TclError:
        # Headless Linux environment without X11/Wayland display server
        return

    window = MarrowAIWindow(root=root)
    assert window is not None
    assert window.model_name.get() != ""
    assert window.download_pct_str.get() == "0.0%"
    assert window.download_progress["value"] == 0.0

    # Test voice profile switching in GUI
    window.voice_profile_var.set("indian_male")
    window._on_voice_changed()
    assert window.voice_engine.profile_name == "indian_male"

    root.destroy()
