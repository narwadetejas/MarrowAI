from __future__ import annotations

import json
import threading
import tkinter as tk
from tkinter import messagebox, ttk
from typing import Any

from .assistant import MarrowAssistant
from .audit import AuditLogger
from .config import get_config
from .governor import ResourceGovernor
from .model import OllamaProvider
from .model_manager import OfflineModelManager
from .voice_engine import OfflineVoiceEngine, VOICE_PROFILES

MODEL_CATALOG = [
    "llama3.2",
    "llama3.2:1b",
    "mistral",
    "phi3",
    "qwen2.5",
    "gemma2",
    "deepseek-r1:7b",
]

# Modern Dark Obsidian Theme Tokens
THEME = {
    "bg_dark": "#0B0F19",
    "surface": "#111827",
    "surface_alt": "#1F2937",
    "surface_elevated": "#283548",
    "border": "#374151",
    "border_highlight": "#4B5563",
    "text_primary": "#F9FAFB",
    "text_secondary": "#9CA3AF",
    "text_muted": "#6B7280",
    "accent_blue": "#2563EB",
    "accent_cyan": "#06B6D4",
    "accent_purple": "#7C3AED",
    "status_green": "#10B981",
    "status_amber": "#F59E0B",
    "status_red": "#EF4444",
}


class MarrowAIWindow:
    """Polished, modern Dark-Mode desktop workstation interface for MarrowAI."""

    def __init__(self, root: tk.Tk | None = None) -> None:
        self.root = root or tk.Tk()
        self.root.title("MarrowAI Workstation — Autonomous Linux Operating Assistant")
        self.root.geometry("1120x760")
        self.root.minsize(920, 620)
        self.root.configure(bg=THEME["bg_dark"])

        self.config = get_config()
        self.model_manager = OfflineModelManager(self.config.ollama_base_url)
        self.governor = ResourceGovernor()
        self.audit = AuditLogger()
        self.voice_engine = OfflineVoiceEngine()

        self.model_name = tk.StringVar(value=self.config.model_name)
        self.status_ollama = tk.StringVar(value="Ollama: Checking...")
        self.status_voice = tk.StringVar(value="Voice: Ready")
        self.status_governor = tk.StringVar(value="Governor: Healthy")
        self.download_pct_str = tk.StringVar(value="0.0%")
        self.download_detail_str = tk.StringVar(value="Ready to pull offline model")
        self.download_bytes_str = tk.StringVar(value="[ 0 MB / 0 MB ]")
        self.speak_responses = tk.BooleanVar(value=True)
        self.voice_profile_var = tk.StringVar(value=self.voice_engine.profile_name)

        self.assistant = MarrowAssistant(
            model_provider=OllamaProvider(self.config.ollama_base_url, self.config.model_name)
        )

        self._configure_styles()
        self._build_layout()
        self._refresh_models()
        self._refresh_telemetry()

    def _configure_styles(self) -> None:
        style = ttk.Style(self.root)
        try:
            style.theme_use("clam")
        except Exception:
            pass

        # Dark theme customizations for ttk widgets
        style.configure("TFrame", background=THEME["bg_dark"])
        style.configure("Surface.TFrame", background=THEME["surface"])
        style.configure("SurfaceAlt.TFrame", background=THEME["surface_alt"])

        style.configure(
            "TLabelframe",
            background=THEME["surface"],
            foreground=THEME["text_primary"],
            bordercolor=THEME["border"],
            relief="solid",
            borderwidth=1,
        )
        style.configure(
            "TLabelframe.Label",
            background=THEME["surface"],
            foreground=THEME["accent_cyan"],
            font=("Segoe UI", 10, "bold"),
        )

        style.configure(
            "TLabel",
            background=THEME["surface"],
            foreground=THEME["text_primary"],
            font=("Segoe UI", 9),
        )
        style.configure(
            "Header.TLabel",
            background=THEME["bg_dark"],
            foreground=THEME["text_primary"],
            font=("Segoe UI", 16, "bold"),
        )
        style.configure(
            "SubHeader.TLabel",
            background=THEME["bg_dark"],
            foreground=THEME["text_secondary"],
            font=("Segoe UI", 9),
        )
        style.configure(
            "Metric.TLabel",
            background=THEME["surface_alt"],
            foreground=THEME["text_primary"],
            font=("Segoe UI", 11, "bold"),
        )
        style.configure(
            "MetricTitle.TLabel",
            background=THEME["surface_alt"],
            foreground=THEME["text_secondary"],
            font=("Segoe UI", 8),
        )

        # Buttons
        style.configure(
            "Primary.TButton",
            background=THEME["accent_blue"],
            foreground="#FFFFFF",
            font=("Segoe UI", 9, "bold"),
            borderwidth=0,
            padding=(12, 6),
        )
        style.map("Primary.TButton", background=[("active", "#1D4ED8")])

        style.configure(
            "Action.TButton",
            background=THEME["surface_alt"],
            foreground=THEME["text_primary"],
            font=("Segoe UI", 9),
            borderwidth=1,
            bordercolor=THEME["border"],
            padding=(10, 5),
        )
        style.map("Action.TButton", background=[("active", THEME["surface_elevated"])])

        style.configure(
            "Download.TButton",
            background=THEME["status_green"],
            foreground="#FFFFFF",
            font=("Segoe UI", 9, "bold"),
            borderwidth=0,
            padding=(12, 6),
        )
        style.map("Download.TButton", background=[("active", "#059669")])

        style.configure(
            "TCheckbutton",
            background=THEME["surface"],
            foreground=THEME["text_primary"],
            font=("Segoe UI", 9),
        )

        # Progress bar
        style.configure(
            "Determinate.Horizontal.TProgressbar",
            troughcolor=THEME["surface_alt"],
            background=THEME["accent_cyan"],
            lightcolor=THEME["accent_cyan"],
            darkcolor=THEME["accent_blue"],
            bordercolor=THEME["border"],
            thickness=16,
        )

    def _build_layout(self) -> None:
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=1)

        # Top Header Deck
        header_frame = tk.Frame(self.root, bg=THEME["bg_dark"], padx=18, pady=12)
        header_frame.grid(row=0, column=0, sticky="ew")
        header_frame.columnconfigure(1, weight=1)

        title_box = tk.Frame(header_frame, bg=THEME["bg_dark"])
        title_box.grid(row=0, column=0, sticky="w")
        tk.Label(
            title_box,
            text="⚡ MarrowAI Workstation",
            bg=THEME["bg_dark"],
            fg=THEME["text_primary"],
            font=("Segoe UI", 16, "bold"),
        ).pack(anchor="w")
        tk.Label(
            title_box,
            text="Autonomous Linux Operating Assistant • Offline-First",
            bg=THEME["bg_dark"],
            fg=THEME["text_secondary"],
            font=("Segoe UI", 9),
        ).pack(anchor="w")

        # Top Status Pills
        status_bar = tk.Frame(header_frame, bg=THEME["bg_dark"])
        status_bar.grid(row=0, column=1, sticky="e")

        self.pill_ollama = tk.Label(
            status_bar,
            textvariable=self.status_ollama,
            bg=THEME["surface_alt"],
            fg=THEME["status_green"],
            font=("Segoe UI", 9, "bold"),
            padx=10,
            pady=4,
            relief="solid",
            bd=1,
        )
        self.pill_ollama.pack(side="left", padx=4)

        self.pill_governor = tk.Label(
            status_bar,
            textvariable=self.status_governor,
            bg=THEME["surface_alt"],
            fg=THEME["accent_cyan"],
            font=("Segoe UI", 9, "bold"),
            padx=10,
            pady=4,
            relief="solid",
            bd=1,
        )
        self.pill_governor.pack(side="left", padx=4)

        self.pill_voice = tk.Label(
            status_bar,
            textvariable=self.status_voice,
            bg=THEME["surface_alt"],
            fg=THEME["accent_purple"],
            font=("Segoe UI", 9, "bold"),
            padx=10,
            pady=4,
            relief="solid",
            bd=1,
        )
        self.pill_voice.pack(side="left", padx=4)

        # Main Body Split (Left Sidebar 340px, Right Center Area)
        body = tk.Frame(self.root, bg=THEME["bg_dark"], padx=16, pady=4)
        body.grid(row=1, column=0, sticky="nsew")
        body.columnconfigure(1, weight=1)
        body.rowconfigure(0, weight=1)

        # LEFT SIDEBAR
        sidebar = tk.Frame(body, bg=THEME["surface"], width=320, padx=12, pady=12, highlightbackground=THEME["border"], highlightthickness=1)
        sidebar.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        sidebar.grid_propagate(False)

        # 1. System Telemetry & Governor Card
        tk.Label(sidebar, text="📊 SYSTEM TELEMETRY", bg=THEME["surface"], fg=THEME["accent_cyan"], font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(0, 6))
        telemetry_box = tk.Frame(sidebar, bg=THEME["surface_alt"], padx=10, pady=8, highlightbackground=THEME["border"], highlightthickness=1)
        telemetry_box.pack(fill="x", pady=(0, 12))

        self.lbl_cpu = tk.Label(telemetry_box, text="CPU: 0.0%", bg=THEME["surface_alt"], fg=THEME["text_primary"], font=("Segoe UI", 9))
        self.lbl_cpu.pack(anchor="w")
        self.lbl_mem = tk.Label(telemetry_box, text="Free RAM: Checking...", bg=THEME["surface_alt"], fg=THEME["text_primary"], font=("Segoe UI", 9))
        self.lbl_mem.pack(anchor="w")
        self.lbl_hyp = tk.Label(telemetry_box, text="Hypervisors: Detecting...", bg=THEME["surface_alt"], fg=THEME["text_secondary"], font=("Segoe UI", 8))
        self.lbl_hyp.pack(anchor="w", pady=(2, 0))

        # 2. Autonomous Quick Actions
        tk.Label(sidebar, text="⚡ QUICK WORKFLOWS", bg=THEME["surface"], fg=THEME["accent_cyan"], font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(6, 6))

        actions_frame = tk.Frame(sidebar, bg=THEME["surface"])
        actions_frame.pack(fill="x", pady=(0, 12))

        btn_arch = tk.Button(actions_frame, text="🚀 Create Arch Linux VM", bg=THEME["surface_alt"], fg=THEME["text_primary"], relief="flat", padx=8, pady=5, font=("Segoe UI", 9), anchor="w", command=lambda: self._quick_action("create an arch linux vm"))
        btn_arch.pack(fill="x", pady=2)

        btn_ubuntu = tk.Button(actions_frame, text="🐧 Create Ubuntu VM", bg=THEME["surface_alt"], fg=THEME["text_primary"], relief="flat", padx=8, pady=5, font=("Segoe UI", 9), anchor="w", command=lambda: self._quick_action("download a virtual machine and create an ubuntu os in vm"))
        btn_ubuntu.pack(fill="x", pady=2)

        btn_status = tk.Button(actions_frame, text="🔍 Full Telemetry & Health", bg=THEME["surface_alt"], fg=THEME["text_primary"], relief="flat", padx=8, pady=5, font=("Segoe UI", 9), anchor="w", command=lambda: self._quick_action("what is the system status and health?"))
        btn_status.pack(fill="x", pady=2)

        btn_tests = tk.Button(actions_frame, text="🧪 Run Local Test Suite", bg=THEME["surface_alt"], fg=THEME["text_primary"], relief="flat", padx=8, pady=5, font=("Segoe UI", 9), anchor="w", command=lambda: self._quick_action("test the project code"))
        btn_tests.pack(fill="x", pady=2)

        btn_audit = tk.Button(actions_frame, text="📋 View Security Audit Log", bg=THEME["surface_alt"], fg=THEME["text_primary"], relief="flat", padx=8, pady=5, font=("Segoe UI", 9), anchor="w", command=self._show_audit_modal)
        btn_audit.pack(fill="x", pady=2)

        # 3. Voice & Speech Settings
        tk.Label(sidebar, text="🎙️ VOICE PROFILE", bg=THEME["surface"], fg=THEME["accent_cyan"], font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(6, 6))
        voice_box = tk.Frame(sidebar, bg=THEME["surface_alt"], padx=10, pady=8, highlightbackground=THEME["border"], highlightthickness=1)
        voice_box.pack(fill="x", pady=(0, 6))

        voice_choices = ["indian_female", "indian_male"]
        self.voice_combo = ttk.Combobox(voice_box, textvariable=self.voice_profile_var, values=voice_choices, state="readonly", width=18)
        self.voice_combo.pack(fill="x", pady=(0, 6))
        self.voice_combo.bind("<<ComboboxSelected>>", lambda _e: self._on_voice_changed())

        chk_speak = tk.Checkbutton(voice_box, text="Speak responses", variable=self.speak_responses, bg=THEME["surface_alt"], fg=THEME["text_primary"], selectcolor=THEME["surface"], activebackground=THEME["surface_alt"], activeforeground=THEME["text_primary"], font=("Segoe UI", 9))
        chk_speak.pack(anchor="w")

        btn_test_voice = tk.Button(voice_box, text="🔊 Test Voice Output", bg=THEME["surface"], fg=THEME["accent_purple"], relief="flat", padx=8, pady=4, font=("Segoe UI", 9, "bold"), command=self._test_voice)
        btn_test_voice.pack(fill="x", pady=(6, 0))

        # RIGHT MAIN WORKSPACE (Chat + Model Management Hub)
        main_workspace = tk.Frame(body, bg=THEME["bg_dark"])
        main_workspace.grid(row=0, column=1, sticky="nsew")
        main_workspace.columnconfigure(0, weight=1)
        main_workspace.rowconfigure(0, weight=1)

        # Chat Workspace Card
        chat_card = tk.Frame(main_workspace, bg=THEME["surface"], padx=14, pady=12, highlightbackground=THEME["border"], highlightthickness=1)
        chat_card.grid(row=0, column=0, sticky="nsew", pady=(0, 10))
        chat_card.columnconfigure(0, weight=1)
        chat_card.rowconfigure(0, weight=1)

        # Output text view with scrollbar
        self.output = tk.Text(
            chat_card,
            wrap="word",
            state="disabled",
            bg=THEME["bg_dark"],
            fg=THEME["text_primary"],
            insertbackground=THEME["accent_cyan"],
            relief="flat",
            font=("Segoe UI", 10),
            padx=12,
            pady=10,
        )
        self.output.grid(row=0, column=0, sticky="nsew")
        scrollbar = ttk.Scrollbar(chat_card, orient="vertical", command=self.output.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.output.configure(yscrollcommand=scrollbar.set)

        # Tag configurations for chat messages
        self.output.tag_configure("user", foreground=THEME["accent_cyan"], font=("Segoe UI", 10, "bold"))
        self.output.tag_configure("narration", foreground=THEME["status_amber"], font=("Segoe UI", 9, "italic"))
        self.output.tag_configure("marrow", foreground=THEME["text_primary"], font=("Segoe UI", 10))
        self.output.tag_configure("success", foreground=THEME["status_green"], font=("Segoe UI", 10, "bold"))
        self.output.tag_configure("blocked", foreground=THEME["status_red"], font=("Segoe UI", 10, "bold"))

        # Prompt Entry Row
        prompt_box = tk.Frame(chat_card, bg=THEME["surface"], pady=10)
        prompt_box.grid(row=1, column=0, columnspan=2, sticky="ew")
        prompt_box.columnconfigure(0, weight=1)

        self.prompt = tk.Entry(
            prompt_box,
            bg=THEME["bg_dark"],
            fg=THEME["text_primary"],
            insertbackground=THEME["accent_cyan"],
            relief="flat",
            font=("Segoe UI", 11),
            highlightbackground=THEME["border"],
            highlightthickness=1,
        )
        self.prompt.grid(row=0, column=0, sticky="ew", padx=(0, 8), ipady=6)
        self.prompt.bind("<Return>", lambda _event: self._send_message())

        btn_send = tk.Button(
            prompt_box,
            text="Send Request",
            bg=THEME["accent_blue"],
            fg="#FFFFFF",
            font=("Segoe UI", 9, "bold"),
            relief="flat",
            padx=14,
            pady=6,
            command=self._send_message,
        )
        btn_send.grid(row=0, column=1, padx=(0, 6))

        btn_mic = tk.Button(
            prompt_box,
            text="🎙️ Voice",
            bg=THEME["surface_alt"],
            fg=THEME["text_primary"],
            font=("Segoe UI", 9),
            relief="flat",
            padx=10,
            pady=6,
            command=self._trigger_voice_input,
        )
        btn_mic.grid(row=0, column=2, padx=(0, 6))

        btn_clear = tk.Button(
            prompt_box,
            text="Clear",
            bg=THEME["surface_alt"],
            fg=THEME["text_secondary"],
            font=("Segoe UI", 9),
            relief="flat",
            padx=10,
            pady=6,
            command=self._clear_chat,
        )
        btn_clear.grid(row=0, column=3)

        # BOTTOM MODEL MANAGEMENT HUB
        model_card = tk.Frame(main_workspace, bg=THEME["surface"], padx=14, pady=12, highlightbackground=THEME["border"], highlightthickness=1)
        model_card.grid(row=1, column=0, sticky="ew")
        model_card.columnconfigure(1, weight=1)

        header_row = tk.Frame(model_card, bg=THEME["surface"])
        header_row.grid(row=0, column=0, columnspan=4, sticky="ew", pady=(0, 8))
        tk.Label(header_row, text="📦 LOCAL OFFLINE MODEL MANAGER", bg=THEME["surface"], fg=THEME["accent_cyan"], font=("Segoe UI", 9, "bold")).pack(side="left")
        self.lbl_pct = tk.Label(header_row, textvariable=self.download_pct_str, bg=THEME["surface"], fg=THEME["status_green"], font=("Segoe UI", 12, "bold"))
        self.lbl_pct.pack(side="right")

        tk.Label(model_card, text="Model:", bg=THEME["surface"], fg=THEME["text_secondary"], font=("Segoe UI", 9)).grid(row=1, column=0, sticky="w", padx=(0, 8))

        self.model_selector = ttk.Combobox(model_card, textvariable=self.model_name, values=MODEL_CATALOG, state="normal", width=28)
        self.model_selector.grid(row=1, column=1, sticky="ew", padx=(0, 10))

        btn_refresh = tk.Button(model_card, text="🔄 Refresh", bg=THEME["surface_alt"], fg=THEME["text_primary"], relief="flat", padx=10, pady=4, font=("Segoe UI", 9), command=self._refresh_models)
        btn_refresh.grid(row=1, column=2, padx=(0, 6))

        self.btn_download = tk.Button(model_card, text="⬇ Download Model", bg=THEME["status_green"], fg="#FFFFFF", relief="flat", padx=14, pady=4, font=("Segoe UI", 9, "bold"), command=self._download_model)
        self.btn_download.grid(row=1, column=3)

        # Real-time Progress Bar (Determinate)
        self.download_progress = ttk.Progressbar(model_card, mode="determinate", maximum=100.0, style="Determinate.Horizontal.TProgressbar")
        self.download_progress.grid(row=2, column=0, columnspan=4, sticky="ew", pady=(10, 4))

        # Progress Detail Row
        prog_detail = tk.Frame(model_card, bg=THEME["surface"])
        prog_detail.grid(row=3, column=0, columnspan=4, sticky="ew")
        tk.Label(prog_detail, textvariable=self.download_detail_str, bg=THEME["surface"], fg=THEME["text_secondary"], font=("Segoe UI", 8)).pack(side="left")
        tk.Label(prog_detail, textvariable=self.download_bytes_str, bg=THEME["surface"], fg=THEME["accent_cyan"], font=("Segoe UI", 8, "bold")).pack(side="right")

        welcome_msg = (
            "MarrowAI Workstation initialized.\n"
            "I am your offline-first Linux operating assistant with deterministic planning and safety governance.\n"
            "Select any action from the left sidebar, download an offline AI model, or type your request below."
        )
        self._append(welcome_msg, "marrow")

    def _append(self, text: str, tag: str = "marrow") -> None:
        self.output.configure(state="normal")
        self.output.insert("end", text + "\n", tag)
        self.output.configure(state="disabled")
        self.output.see("end")

    def _clear_chat(self) -> None:
        self.output.configure(state="normal")
        self.output.delete("1.0", "end")
        self.output.configure(state="disabled")

    def _safe_after(self, fn: Any) -> None:
        try:
            if self.root and self.root.winfo_exists():
                self.root.after(0, fn)
        except Exception:
            pass

    def _refresh_telemetry(self) -> None:
        def work() -> None:
            healthy, gov_info = self.governor.is_safe_to_execute()
            status_text = "Governor: Healthy" if healthy else "Governor: Guarded"
            tel = self.governor.get_telemetry()
            load1 = tel.load_average[0] if tel.load_average else 0.0
            cpu_val = f"CPU Load: {load1:.2f} (1m) | {tel.cpu_percent:.1f}%"
            mem_val = f"Free RAM: {tel.memory_available_mb:.0f} MB"

            from .vm_manager import VMManager
            mgr = VMManager()
            detected = mgr.detect_hypervisors()
            hyp_str = f"Hypervisors: {detected['recommended']}"

            self._safe_after(lambda: self._update_telemetry_ui(status_text, cpu_val, mem_val, hyp_str))

        threading.Thread(target=work, daemon=True).start()

    def _update_telemetry_ui(self, gov_status: str, cpu_str: str, mem_str: str, hyp_str: str) -> None:
        self.status_governor.set(gov_status)
        self.lbl_cpu.configure(text=cpu_str)
        self.lbl_mem.configure(text=mem_str)
        self.lbl_hyp.configure(text=hyp_str)

    def _refresh_models(self) -> None:
        def work() -> None:
            available = self.model_manager.is_available()
            models = self.model_manager.list_local_models() if available else []
            self._safe_after(lambda: self._show_models(available, models))

        threading.Thread(target=work, daemon=True).start()

    def _show_models(self, available: bool, models: list[str]) -> None:
        self.status_ollama.set("Ollama: ONLINE" if available else "Ollama: OFFLINE")
        self.pill_ollama.configure(fg=THEME["status_green"] if available else THEME["status_amber"])
        installed_items = [f"✓ {m} (Installed)" for m in models]
        catalog_items = [f"⬇ {m} (Download)" for m in MODEL_CATALOG if m not in models]
        choices = installed_items + catalog_items
        self.model_selector["values"] = choices
        if models:
            current = self.model_name.get()
            matched = next((m for m in models if m in current or current in m), models[0])
            self.model_name.set(f"✓ {matched} (Installed)")
            if hasattr(self.assistant.model_provider, "model"):
                self.assistant.model_provider.model = matched
        elif choices:
            self.model_name.set(choices[0])
        prof_label = VOICE_PROFILES.get(self.voice_engine.profile_name, {}).get("label", "Indian English")
        self.status_voice.set(f"Voice: {prof_label}")

    def _on_voice_changed(self) -> None:
        selected = self.voice_profile_var.get().strip()
        if selected in VOICE_PROFILES:
            self.voice_engine.set_profile(selected)
            prof_label = VOICE_PROFILES[selected]["label"]
            self.status_voice.set(f"Voice: {prof_label}")
            ack = f"Voice profile switched to {prof_label}."
            self._append(f"[Voice] {ack}", "narration")
            if self.speak_responses.get():
                threading.Thread(target=self.voice_engine.speak, args=(ack,), daemon=True).start()

    def _test_voice(self) -> None:
        text = "Namaste. I am MarrowAI, your offline-first Linux operating assistant."
        threading.Thread(target=self.voice_engine.speak, args=(text,), daemon=True).start()

    def _download_model(self) -> None:
        raw_name = self.model_name.get().strip()
        clean_name = raw_name.replace("✓ ", "").replace("⬇ ", "").split(" (")[0].strip()
        if not clean_name:
            messagebox.showerror("Model required", "Please enter or select a model name.")
            return
        model_name = clean_name

        self.btn_download.configure(state="disabled", text="Downloading...")
        self.download_pct_str.set("0.0%")
        self.download_progress["value"] = 0.0
        self.download_detail_str.set(f"Initializing download of {model_name}...")
        self._append(f"[Model Download] Starting download of '{model_name}'...", "narration")

        def on_progress(pct: float, detail: str, completed: int, total: int) -> None:
            def update_ui() -> None:
                self.download_progress["value"] = pct
                self.download_pct_str.set(f"{pct:.1f}%")
                self.download_detail_str.set(detail)
                if total > 0:
                    c_mb = completed / (1024 * 1024)
                    t_mb = total / (1024 * 1024)
                    self.download_bytes_str.set(f"[ {c_mb:.1f} MB / {t_mb:.1f} MB ]")
            self._safe_after(update_ui)

        def work() -> None:
            success, message = self.model_manager.download_model(
                model_name,
                progress_callback=on_progress,
                voice_notify=self.speak_responses.get(),
            )
            self._safe_after(lambda: self._download_finished(model_name, success, message))

        threading.Thread(target=work, daemon=True).start()

    def _download_finished(self, model_name: str, success: bool, message: str) -> None:
        self.btn_download.configure(state="normal", text="⬇ Download Model")
        if success:
            self.download_pct_str.set("100.0%")
            self.download_progress["value"] = 100.0
            self.download_detail_str.set(f"Model '{model_name}' downloaded and verified locally.")
            self._append(f"[Model Download] Success: {message}", "success")
            self._refresh_models()
        else:
            self.download_detail_str.set(f"Download failed: {message}")
            self._append(f"[Model Download] Failed: {message}", "blocked")
            messagebox.showerror("Model Download", message)

    def _quick_action(self, prompt: str) -> None:
        self.prompt.delete(0, "end")
        self.prompt.insert(0, prompt)
        self._send_message()

    def _send_message(self) -> None:
        text = self.prompt.get().strip()
        if not text:
            return
        self.prompt.delete(0, "end")
        self._append(f"\nYou: {text}", "user")

        self.assistant.model_provider = OllamaProvider(
            self.config.ollama_base_url, self.model_name.get().strip() or self.config.model_name
        )

        def on_narration(msg: str) -> None:
            def update_ui() -> None:
                self._append(f"🔊 Spoken Action: {msg}", "narration")
            self._safe_after(update_ui)
            if self.speak_responses.get():
                threading.Thread(target=self.voice_engine.speak, args=(msg,), daemon=True).start()

        def work() -> None:
            result = self.assistant.process(text, on_narration=on_narration)
            self._safe_after(lambda: self._show_result(result))

        threading.Thread(target=work, daemon=True).start()

    def _show_result(self, result: dict) -> None:
        decision = result.get("decision", "ALLOW")
        status = result.get("status", "unknown")
        output = result.get("output", "")

        if status == "requires_confirmation":
            conf_msg = output or "⚠️ This high-risk task requires explicit authorization to execute."
            self._append(f"MarrowAI [SECURITY GATE]: {conf_msg}", "blocked")
            if self.speak_responses.get():
                threading.Thread(target=self.voice_engine.speak, args=("This action requires confirmation.",), daemon=True).start()
            confirmed = messagebox.askyesno(
                "Security Authorization Required",
                f"{conf_msg}\n\nDo you authorize MarrowAI to execute this action?",
                parent=self.root,
            )
            if confirmed:
                def confirm_work() -> None:
                    res = self.assistant.process("yes", confirmed=True)
                    self._safe_after(lambda: self._show_result(res))
                threading.Thread(target=confirm_work, daemon=True).start()
            else:
                self._append("MarrowAI: Action cancelled by user.", "narration")
            return

        if decision == "DENY":
            msg = "Action was blocked by safety policy (MA-CORE-002)."
            self._append(f"MarrowAI: {msg}", "blocked")
            if self.speak_responses.get():
                threading.Thread(target=self.voice_engine.speak, args=(msg,), daemon=True).start()
            return

        if status == "blocked":
            msg = f"Task blocked: {output or 'Policy violation or resource governor limit'}"
            self._append(f"MarrowAI: {msg}", "blocked")
            if self.speak_responses.get():
                threading.Thread(target=self.voice_engine.speak, args=(msg,), daemon=True).start()
            return

        if status == "unsupported":
            msg = "That request is outside the currently supported toolset."
            self._append(f"MarrowAI: {msg}", "narration")
            if self.speak_responses.get():
                threading.Thread(target=self.voice_engine.speak, args=(msg,), daemon=True).start()
            return

        if output:
            self._append(f"MarrowAI [Status: {status}]:\n{output}", "marrow")
            is_conversational = result.get("intent") in {
                "explain_arch_linux", "explain_ubuntu", "explain_vm", "explain_models",
                "voice_info", "assistant_info", "greeting", "general_question", "answer_question"
            }
            if self.speak_responses.get() and not is_conversational:
                first_line = output.strip().splitlines()[0] if output.strip() else "Task completed."
                threading.Thread(target=self.voice_engine.speak, args=(first_line[:160],), daemon=True).start()
        else:
            self._append(f"MarrowAI: Task completed with status '{status}'.", "success")

        self._refresh_telemetry()

    def _trigger_voice_input(self) -> None:
        dialog = tk.Toplevel(self.root)
        dialog.title("Voice Input")
        dialog.geometry("450x180")
        dialog.configure(bg=THEME["surface"])
        dialog.transient(self.root)
        dialog.grab_set()

        tk.Label(dialog, text="🎙️ Speak or Transcribe Request", bg=THEME["surface"], fg=THEME["text_primary"], font=("Segoe UI", 12, "bold")).pack(pady=(16, 6))
        tk.Label(dialog, text="Speak your command aloud or enter voice transcription below:", bg=THEME["surface"], fg=THEME["text_secondary"], font=("Segoe UI", 9)).pack(pady=(0, 10))

        entry_voice = tk.Entry(dialog, bg=THEME["bg_dark"], fg=THEME["text_primary"], font=("Segoe UI", 10), insertbackground=THEME["accent_cyan"], relief="flat", highlightbackground=THEME["border"], highlightthickness=1)
        entry_voice.pack(fill="x", padx=20, ipady=4)
        entry_voice.insert(0, "create an arch linux vm")
        entry_voice.focus_set()

        def confirm() -> None:
            val = entry_voice.get().strip()
            dialog.destroy()
            if val:
                self.prompt.delete(0, "end")
                self.prompt.insert(0, val)
                self._send_message()

        btn_ok = tk.Button(dialog, text="Process Voice Request", bg=THEME["accent_blue"], fg="#FFFFFF", font=("Segoe UI", 9, "bold"), relief="flat", padx=12, pady=6, command=confirm)
        btn_ok.pack(pady=12)

    def _show_audit_modal(self) -> None:
        events = self.audit.get_recent_events(limit=25)
        modal = tk.Toplevel(self.root)
        modal.title("Security & Compliance Audit Trail (MA-CORE-009)")
        modal.geometry("780x520")
        modal.configure(bg=THEME["bg_dark"])

        header = tk.Frame(modal, bg=THEME["surface"], padx=14, pady=10)
        header.pack(fill="x")
        tk.Label(header, text="🛡️ Tamper-Evident Security Audit Log", bg=THEME["surface"], fg=THEME["text_primary"], font=("Segoe UI", 12, "bold")).pack(anchor="w")
        tk.Label(header, text="All system actions, tool calls, and credential redacting events are logged chronologically.", bg=THEME["surface"], fg=THEME["text_secondary"], font=("Segoe UI", 8)).pack(anchor="w")

        text_audit = tk.Text(modal, bg=THEME["bg_dark"], fg=THEME["text_primary"], font=("Consolas", 9), relief="flat", padx=10, pady=10)
        text_audit.pack(fill="both", expand=True, padx=12, pady=12)

        if not events:
            text_audit.insert("end", "No security audit events recorded yet.\n")
        else:
            for ev in events:
                ts = ev.get("timestamp", "")
                etype = ev.get("event_type", "UNKNOWN")
                data = json.dumps(ev.get("data", {}), indent=2)
                text_audit.insert("end", f"[{ts}] {etype}\n{data}\n\n")

        text_audit.configure(state="disabled")

    def run(self) -> None:
        self.root.mainloop()


def main() -> None:
    try:
        MarrowAIWindow().run()
    except tk.TclError as exc:
        raise SystemExit(f"Unable to start the GUI. A desktop session is required: {exc}") from exc


if __name__ == "__main__":
    main()
