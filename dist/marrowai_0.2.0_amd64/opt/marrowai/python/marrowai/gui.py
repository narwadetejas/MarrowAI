from __future__ import annotations

import threading
import tkinter as tk
from tkinter import messagebox, ttk
from .assistant import MarrowAssistant
from .config import get_config
from .model import OllamaProvider
from .model_manager import OfflineModelManager
from .voice_engine import OfflineVoiceEngine


MODEL_CATALOG = [
    "llama3.2",
    "llama3.2:1b",
    "mistral",
    "phi3",
    "qwen2.5",
    "gemma2",
    "deepseek-r1:7b",
]


class MarrowAIWindow:
    """Desktop interface for chat, model selection, and offline model setup."""

    def __init__(self, root: tk.Tk | None = None) -> None:
        self.root = root or tk.Tk()
        self.root.title("MarrowAI")
        self.root.geometry("900x650")
        self.root.minsize(700, 500)
        self.config = get_config()
        self.model_manager = OfflineModelManager(self.config.ollama_base_url)
        self.voice_engine = OfflineVoiceEngine()
        self.model_name = tk.StringVar(value=self.config.model_name)
        self.status_text = tk.StringVar(value="Checking local Ollama...")
        self.voice_text = tk.StringVar(value="Checking voice...")
        self.speak_responses = tk.BooleanVar(value=True)
        self.assistant = MarrowAssistant(
            model_provider=OllamaProvider(self.config.ollama_base_url, self.config.model_name)
        )
        self._build_layout()
        self._refresh_models()

    def _build_layout(self) -> None:
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=1)

        header = ttk.Frame(self.root, padding=16)
        header.grid(row=0, column=0, sticky="ew")
        header.columnconfigure(1, weight=1)
        ttk.Label(header, text="MarrowAI", font=("TkDefaultFont", 18, "bold")).grid(row=0, column=0, sticky="w")
        ttk.Label(header, textvariable=self.status_text).grid(row=0, column=1, padx=(20, 0), sticky="w")

        content = ttk.Frame(self.root, padding=(16, 0, 16, 16))
        content.grid(row=1, column=0, sticky="nsew")
        content.columnconfigure(0, weight=1)
        content.rowconfigure(0, weight=1)

        chat = ttk.LabelFrame(content, text="Safe local assistant", padding=10)
        chat.grid(row=0, column=0, sticky="nsew")
        chat.columnconfigure(0, weight=1)
        chat.rowconfigure(0, weight=1)
        self.output = tk.Text(chat, wrap="word", state="disabled", height=20)
        self.output.grid(row=0, column=0, columnspan=2, sticky="nsew")
        scrollbar = ttk.Scrollbar(chat, orient="vertical", command=self.output.yview)
        scrollbar.grid(row=0, column=2, sticky="ns")
        self.output.configure(yscrollcommand=scrollbar.set)
        self.prompt = ttk.Entry(chat)
        self.prompt.grid(row=1, column=0, pady=(10, 0), sticky="ew")
        self.prompt.bind("<Return>", lambda _event: self._send_message())
        ttk.Button(chat, text="Send", command=self._send_message).grid(row=1, column=1, padx=(8, 0), pady=(10, 0))
        ttk.Button(chat, text="Speak", command=self._speak_prompt).grid(row=1, column=2, padx=(8, 0), pady=(10, 0))

        models = ttk.LabelFrame(content, text="Local model", padding=10)
        models.grid(row=1, column=0, pady=(14, 0), sticky="ew")
        models.columnconfigure(1, weight=1)
        ttk.Label(models, text="Model name").grid(row=0, column=0, sticky="w")
        self.model_selector = ttk.Combobox(models, textvariable=self.model_name, state="normal", values=MODEL_CATALOG)
        self.model_selector.grid(row=0, column=1, padx=8, sticky="ew")
        ttk.Button(models, text="Refresh", command=self._refresh_models).grid(row=0, column=2, padx=(0, 8))
        ttk.Button(models, text="Download", command=self._download_model).grid(row=0, column=3)
        self.download_progress = ttk.Progressbar(models, mode="indeterminate")
        self.download_progress.grid(row=1, column=0, columnspan=4, pady=(10, 0), sticky="ew")
        ttk.Label(models, text="Download once while online; the installed model runs locally afterward.").grid(
            row=2, column=0, columnspan=4, pady=(8, 0), sticky="w"
        )
        ttk.Checkbutton(models, text="Speak responses", variable=self.speak_responses).grid(
            row=3, column=0, columnspan=2, pady=(8, 0), sticky="w"
        )
        ttk.Label(models, textvariable=self.voice_text).grid(row=3, column=2, columnspan=2, pady=(8, 0), sticky="e")

    def _append(self, text: str) -> None:
        self.output.configure(state="normal")
        self.output.insert("end", text + "\n")
        self.output.configure(state="disabled")
        self.output.see("end")

    def _refresh_models(self) -> None:
        def work() -> None:
            available = self.model_manager.is_available()
            models = self.model_manager.list_local_models() if available else []
            self.root.after(0, lambda: self._show_models(available, models))

        threading.Thread(target=work, daemon=True).start()

    def _show_models(self, available: bool, models: list[str]) -> None:
        self.status_text.set("Ollama online" if available else "Ollama offline; text fallback available")
        choices = list(dict.fromkeys(MODEL_CATALOG + models))
        self.model_selector["values"] = choices
        if models and self.model_name.get() not in models:
            self.model_name.set(models[0])
        self.voice_text.set(self._voice_summary())

    def _voice_summary(self) -> str:
        status = self.voice_engine.status()
        tts = status["tts_backend"]
        stt = status["stt_backend"]
        if tts == "fallback":
            return "Voice output unavailable"
        return f"Voice output: {tts}; microphone input: {stt} pipeline"

    def _download_model(self) -> None:
        model_name = self.model_name.get().strip()
        if not model_name:
            messagebox.showerror("Model name required", "Enter an Ollama model name first.")
            return
        self.download_progress.start(12)
        self.status_text.set(f"Downloading {model_name}...")

        def work() -> None:
            success, message = self.model_manager.download_model(model_name)
            self.root.after(0, lambda: self._download_finished(model_name, success, message))

        threading.Thread(target=work, daemon=True).start()

    def _download_finished(self, model_name: str, success: bool, message: str) -> None:
        self.download_progress.stop()
        if success:
            self.status_text.set(f"{model_name} installed locally")
            self._refresh_models()
        else:
            self.status_text.set("Model download needs attention")
            messagebox.showerror("Model download", message)

    def _send_message(self) -> None:
        text = self.prompt.get().strip()
        if not text:
            return
        self.prompt.delete(0, "end")
        self._append(f"You: {text}")
        self._append("MarrowAI: Checking the request and safety policy...")

        self.assistant.model_provider = OllamaProvider(
            self.config.ollama_base_url, self.model_name.get().strip() or self.config.model_name
        )

        def work() -> None:
            result = self.assistant.process(text)
            self.root.after(0, lambda: self._show_result(result))

        threading.Thread(target=work, daemon=True).start()

    def _show_result(self, result: dict) -> None:
        if result.get("decision") == "DENY":
            response = "Action blocked by safety policy."
        elif result.get("status") == "unsupported":
            response = "That task is not supported by the current safe tool set."
        else:
            response = str(result.get("output") or result.get("status") or "No result")
        self._append(f"MarrowAI: {response}")
        if self.speak_responses.get() and response:
            threading.Thread(target=self.voice_engine.speak, args=(response,), daemon=True).start()

    def _speak_prompt(self) -> None:
        text = self.prompt.get().strip()
        if not text:
            return
        threading.Thread(target=self.voice_engine.speak, args=(text,), daemon=True).start()

    def run(self) -> None:
        self.root.mainloop()


def main() -> None:
    try:
        MarrowAIWindow().run()
    except tk.TclError as exc:
        raise SystemExit(f"Unable to start the GUI. A desktop session is required: {exc}") from exc


if __name__ == "__main__":
    main()
