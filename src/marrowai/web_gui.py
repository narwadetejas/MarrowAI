from __future__ import annotations

import json
import threading
import urllib.parse
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any

from .assistant import MarrowAssistant
from .audit import AuditLogger
from .config import get_config
from .governor import ResourceGovernor
from .model import OllamaProvider
from .model_manager import OfflineModelManager
from .voice_engine import OfflineVoiceEngine, VOICE_PROFILES

HTML_PAGE = r"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>MarrowAI — Autonomous Linux Operating Assistant</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
  <style>
    :root {
      --bg: #080a0f;
      --bg-gradient: radial-gradient(ellipse 80% 50% at 50% -20%, rgba(99, 102, 241, 0.12), transparent 70%), #080a0f;
      --surface: #0e131f;
      --surface-elevated: #141b2d;
      --surface-glass: rgba(16, 22, 36, 0.75);
      --card-border: rgba(255, 255, 255, 0.07);
      --card-border-hover: rgba(255, 255, 255, 0.15);
      --card-border-focus: rgba(99, 102, 241, 0.5);
      --accent: #6366f1;
      --accent-gradient: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
      --accent-cyan: #38bdf8;
      --status-green: #10b981;
      --status-amber: #f59e0b;
      --status-red: #f43f5e;
      --text-main: #f8fafc;
      --text-muted: #94a3b8;
      --text-dim: #64748b;
      --shadow-sm: 0 2px 8px rgba(0, 0, 0, 0.3);
      --shadow-md: 0 8px 30px rgba(0, 0, 0, 0.5);
      --shadow-accent: 0 0 25px rgba(99, 102, 241, 0.25);
    }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
      background: var(--bg-gradient);
      color: var(--text-main);
      min-height: 100vh;
      display: flex;
      flex-direction: column;
      overflow-x: hidden;
      line-height: 1.5;
    }
    header {
      padding: 14px 28px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      border-bottom: 1px solid var(--card-border);
      backdrop-filter: blur(20px);
      -webkit-backdrop-filter: blur(20px);
      background: rgba(10, 14, 23, 0.75);
      position: sticky;
      top: 0;
      z-index: 100;
    }
    .brand-container { display: flex; align-items: center; gap: 14px; }
    .brand-logo {
      width: 36px; height: 36px;
      border-radius: 10px;
      background: var(--accent-gradient);
      display: flex; align-items: center; justify-content: center;
      box-shadow: var(--shadow-accent);
    }
    .brand-logo svg { width: 20px; height: 20px; fill: none; stroke: #fff; stroke-width: 2.2; stroke-linecap: round; stroke-linejoin: round; }
    .brand-title { display: flex; flex-direction: column; }
    .brand-name {
      font-size: 1.15rem; font-weight: 700; letter-spacing: -0.3px;
      display: flex; align-items: center; gap: 8px;
    }
    .brand-badge {
      font-size: 0.65rem; font-weight: 700; text-transform: uppercase;
      letter-spacing: 0.8px; padding: 2px 7px; border-radius: 6px;
      background: rgba(99, 102, 241, 0.18); border: 1px solid rgba(99, 102, 241, 0.35);
      color: #a5b4fc;
    }
    .brand-desc { font-size: 0.72rem; color: var(--text-muted); }

    .header-actions { display: flex; gap: 10px; align-items: center; }
    .active-model-pill {
      display: flex; align-items: center; gap: 8px;
      padding: 5px 12px; border-radius: 20px;
      background: rgba(255, 255, 255, 0.04);
      border: 1px solid var(--card-border);
      font-size: 0.78rem; font-weight: 600;
      color: var(--text-main); cursor: pointer;
      transition: all 0.2s ease;
    }
    .active-model-pill:hover { border-color: var(--card-border-hover); background: rgba(255, 255, 255, 0.07); }
    .pill {
      font-size: 0.74rem; font-weight: 600; padding: 5px 12px; border-radius: 20px;
      background: rgba(255, 255, 255, 0.04); border: 1px solid var(--card-border);
      display: flex; align-items: center; gap: 6px;
    }
    .pill.green { color: var(--status-green); border-color: rgba(16, 185, 129, 0.25); background: rgba(16, 185, 129, 0.08); }
    .pill.amber { color: var(--status-amber); border-color: rgba(245, 158, 11, 0.25); background: rgba(245, 158, 11, 0.08); }
    .pill.indigo { color: #818cf8; border-color: rgba(99, 102, 241, 0.25); background: rgba(99, 102, 241, 0.08); }
    .dot { width: 6px; height: 6px; border-radius: 50%; background: currentColor; }

    /* Soundwave visualizer */
    .sound-wave {
      display: inline-flex; align-items: center; gap: 2px; height: 12px;
    }
    .sound-wave span {
      display: block; width: 2px; height: 100%; border-radius: 1px;
      background: currentColor;
    }
    .sound-wave.active span {
      animation: wave 1s ease-in-out infinite alternate;
    }
    .sound-wave.active span:nth-child(2) { animation-delay: 0.2s; }
    .sound-wave.active span:nth-child(3) { animation-delay: 0.4s; }
    .sound-wave.active span:nth-child(4) { animation-delay: 0.6s; }
    @keyframes wave {
      0% { height: 3px; }
      100% { height: 12px; }
    }

    main {
      flex: 1; display: grid; grid-template-columns: 310px 1fr; gap: 24px;
      padding: 24px 28px; max-width: 1600px; margin: 0 auto; width: 100%;
    }
    .sidebar { display: flex; flex-direction: column; gap: 18px; }
    .card {
      background: var(--surface-glass);
      border: 1px solid var(--card-border);
      border-radius: 16px;
      padding: 18px;
      backdrop-filter: blur(16px);
      -webkit-backdrop-filter: blur(16px);
      transition: border-color 0.2s, box-shadow 0.2s;
    }
    .card:hover { border-color: var(--card-border-hover); }
    .card-title {
      font-size: 0.72rem; font-weight: 700; text-transform: uppercase;
      letter-spacing: 0.9px; color: var(--text-muted); margin-bottom: 12px;
      display: flex; align-items: center; justify-content: space-between;
    }
    .card-title svg { width: 14px; height: 14px; opacity: 0.7; }
    .metric-row { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; font-size: 0.83rem; }
    .metric-label { color: var(--text-muted); }
    .metric-val { font-family: 'JetBrains Mono', monospace; font-weight: 600; color: #fff; }

    .action-btn {
      width: 100%; padding: 9px 12px; border-radius: 10px;
      border: 1px solid var(--card-border); background: rgba(255, 255, 255, 0.02);
      color: var(--text-main); font-family: inherit; font-size: 0.83rem; font-weight: 500;
      text-align: left; cursor: pointer; display: flex; align-items: center; gap: 10px;
      margin-bottom: 6px; transition: all 0.2s;
    }
    .action-btn svg { width: 15px; height: 15px; flex-shrink: 0; color: var(--accent-cyan); stroke-width: 2; }
    .action-btn:hover {
      background: rgba(99, 102, 241, 0.1); border-color: rgba(99, 102, 241, 0.3);
      color: #fff; transform: translateX(2px);
    }

    .select-box, input[type="text"], input[type="password"] {
      width: 100%; padding: 9px 12px; border-radius: 10px;
      border: 1px solid var(--card-border); background: rgba(0, 0, 0, 0.35);
      color: var(--text-main); font-family: inherit; font-size: 0.85rem;
      outline: none; transition: border-color 0.2s, box-shadow 0.2s;
    }
    .select-box:focus, input[type="text"]:focus, input[type="password"]:focus {
      border-color: var(--accent); box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.2);
    }
    .select-box optgroup {
      background: var(--surface-elevated);
      color: #a5b4fc;
      font-weight: 700;
    }
    .select-box option {
      background: #0e131f;
      color: var(--text-main);
      padding: 6px 10px;
    }

    .workspace { display: flex; flex-direction: column; gap: 18px; height: 100%; }
    .chat-card {
      flex: 1; display: flex; flex-direction: column; min-height: 480px; max-height: 560px;
      position: relative;
    }
    .chat-box {
      flex: 1; overflow-y: auto;
      display: flex; flex-direction: column; gap: 14px; padding-right: 8px;
    }
    .chat-box::-webkit-scrollbar { width: 6px; }
    .chat-box::-webkit-scrollbar-thumb { background: rgba(255, 255, 255, 0.1); border-radius: 3px; }

    .chat-bubble {
      padding: 14px 18px; border-radius: 14px; max-width: 82%;
      font-size: 0.9rem; line-height: 1.55; position: relative;
    }
    .chat-bubble.user {
      align-self: flex-end; background: #161e31;
      border: 1px solid rgba(99, 102, 241, 0.3); color: #fff;
      border-bottom-right-radius: 4px;
    }
    .chat-bubble.marrow {
      align-self: flex-start; background: rgba(255, 255, 255, 0.035);
      border: 1px solid var(--card-border); color: #e2e8f0;
      border-bottom-left-radius: 4px;
    }
    .chat-bubble.narration {
      align-self: center; background: rgba(99, 102, 241, 0.08);
      border: 1px solid rgba(99, 102, 241, 0.2); color: #c7d2fe;
      font-size: 0.82rem; max-width: 90%; text-align: center; border-radius: 10px;
      padding: 8px 14px;
    }

    .bubble-header {
      display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;
    }
    .badge-tag {
      font-size: 0.68rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.6px;
      display: inline-flex; align-items: center; gap: 5px;
    }
    .badge-tag.user { color: var(--accent-cyan); }
    .badge-tag.marrow { color: #818cf8; }

    .code-block {
      background: #090d16; border: 1px solid rgba(255, 255, 255, 0.08);
      border-radius: 8px; padding: 12px 14px; margin: 10px 0;
      font-family: 'JetBrains Mono', monospace; font-size: 0.82rem;
      position: relative; overflow-x: auto; color: #e2e8f0;
    }
    .copy-code-btn {
      position: absolute; top: 6px; right: 6px;
      padding: 3px 8px; border-radius: 5px;
      background: rgba(255, 255, 255, 0.08); border: 1px solid rgba(255, 255, 255, 0.1);
      color: var(--text-muted); font-size: 0.7rem; cursor: pointer;
      transition: all 0.2s;
    }
    .copy-code-btn:hover { background: rgba(255, 255, 255, 0.16); color: #fff; }

    .input-row { display: flex; gap: 10px; align-items: center; margin-top: 14px; }
    .btn-primary {
      padding: 9px 18px; border-radius: 10px; border: none;
      background: var(--accent-gradient);
      color: #fff; font-family: inherit; font-size: 0.85rem; font-weight: 600;
      cursor: pointer; transition: all 0.2s; box-shadow: var(--shadow-accent);
      display: inline-flex; align-items: center; gap: 8px; white-space: nowrap;
    }
    .btn-primary:hover { opacity: 0.92; transform: translateY(-1px); }
    .btn-primary:disabled { opacity: 0.5; cursor: not-allowed; transform: none; }
    .btn-icon {
      padding: 9px 13px; border-radius: 10px; border: 1px solid var(--card-border);
      background: rgba(255, 255, 255, 0.04); color: #fff; font-family: inherit;
      cursor: pointer; transition: all 0.2s; display: inline-flex; align-items: center; gap: 6px;
      font-size: 0.83rem; font-weight: 500;
    }
    .btn-icon:hover { background: rgba(255, 255, 255, 0.09); border-color: var(--card-border-hover); }
    .btn-icon.recording {
      background: rgba(244, 63, 94, 0.18); border-color: var(--status-red); color: var(--status-red);
      animation: pulse 1.5s infinite;
    }
    @keyframes pulse {
      0% { box-shadow: 0 0 0 0 rgba(244, 63, 94, 0.4); }
      70% { box-shadow: 0 0 0 8px rgba(244, 63, 94, 0); }
      100% { box-shadow: 0 0 0 0 rgba(244, 63, 94, 0); }
    }

    /* Model Hub */
    .model-hub {
      display: flex; flex-direction: column; gap: 12px;
    }
    .progress-bar-bg {
      width: 100%; height: 8px; border-radius: 4px;
      background: rgba(0, 0, 0, 0.4); overflow: hidden; border: 1px solid var(--card-border);
    }
    .progress-fill {
      height: 100%; width: 0%; border-radius: 4px;
      background: linear-gradient(90deg, #6366f1, #10b981);
      transition: width 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    .prog-metrics { display: flex; justify-content: space-between; font-size: 0.78rem; color: var(--text-muted); }
    .prog-pct { font-family: 'JetBrains Mono', monospace; font-weight: 700; color: var(--status-green); font-size: 0.95rem; }

    .model-card-item {
      display: flex; justify-content: space-between; align-items: center;
      background: rgba(255, 255, 255, 0.025); border: 1px solid var(--card-border);
      border-radius: 10px; padding: 10px 14px; font-size: 0.83rem;
      transition: border-color 0.2s;
    }
    .model-card-item:hover { border-color: var(--card-border-hover); }
  </style>
</head>
<body>
  <header>
    <div class="brand-container">
      <div class="brand-logo">
        <svg viewBox="0 0 24 24"><path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/></svg>
      </div>
      <div class="brand-title">
        <div class="brand-name">
          MarrowAI
          <span class="brand-badge">Workstation</span>
        </div>
        <div class="brand-desc">Local Autonomous Linux Operating Assistant</div>
      </div>
    </div>

    <div class="header-actions">
      <div class="active-model-pill" id="active-model-badge" title="Active Model">
        <span class="dot" style="background: var(--status-green);"></span>
        <span id="header-model-name">Checking Model...</span>
      </div>
      <div class="pill green" id="pill-ollama"><span class="dot"></span> Ollama: Online</div>
      <div class="pill indigo" id="pill-voice">
        <div class="sound-wave" id="voice-wave">
          <span></span><span></span><span></span><span></span>
        </div>
        <span id="voice-status-text">Studio Speech</span>
      </div>
      <div class="pill" id="pill-gov"><span class="dot"></span> Governor: Optimal</div>
    </div>
  </header>

  <main>
    <div class="sidebar">
      <div class="card">
        <div class="card-title">
          <span>System Telemetry</span>
          <svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/></svg>
        </div>
        <div class="metric-row"><span class="metric-label">CPU Load:</span><span class="metric-val" id="val-cpu">0.0%</span></div>
        <div class="metric-row"><span class="metric-label">Free RAM:</span><span class="metric-val" id="val-mem">-- MB</span></div>
        <div class="metric-row"><span class="metric-label">Hypervisor:</span><span class="metric-val" id="val-hyp" style="font-size:0.75rem;">Detecting</span></div>
      </div>

      <div class="card">
        <div class="card-title">
          <span>Workflows</span>
          <svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16m-7 6h7"/></svg>
        </div>
        <button class="action-btn" onclick="sendQuick('create an arch linux vm')">
          <svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2zM9 9h6v6H9V9z"/></svg>
          Initialize Arch Linux VM
        </button>
        <button class="action-btn" onclick="sendQuick('download a virtual machine and create an ubuntu os in vm')">
          <svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 12h14M12 5l7 7-7 7"/></svg>
          Deploy Ubuntu Linux VM
        </button>
        <button class="action-btn" onclick="sendQuick('what is the system status and health?')">
          <svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
          Diagnostic Health Check
        </button>
        <button class="action-btn" onclick="sendQuick('test the project code')">
          <svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4"/></svg>
          Execute Test Suite
        </button>
      </div>

      <div class="card">
        <div class="card-title">
          <span>Natural Voice Engine</span>
          <svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z"/></svg>
        </div>
        <select class="select-box" id="voice-select" onchange="changeVoice()" style="margin-bottom:10px;">
          <option value="indian_female">Indian English (Female - Neerja Natural)</option>
          <option value="indian_male">Indian English (Male - Prabhat Natural)</option>
          <option value="hindi_female">Hindi / Indian (Female - Swara Natural)</option>
          <option value="hindi_male">Hindi / Indian (Male - Madhur Natural)</option>
        </select>
        <button class="action-btn" onclick="testVoice()" style="margin-bottom:0;">
          <svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.536 8.464a5 5 0 010 7.072m2.828-9.9a9 9 0 010 12.728M5.586 15H4a1 1 0 01-1-1v-4a1 1 0 011-1h1.586l4.707-4.707C10.923 3.663 12 4.109 12 5v14c0 .891-1.077 1.337-1.707.707L5.586 15z"/></svg>
          Preview Natural Speech
        </button>
      </div>
    </div>

    <div class="workspace">
      <div class="card chat-card">
        <div class="chat-box" id="chat-box">
          <div class="chat-bubble marrow">
            <div class="bubble-header">
              <span class="badge-tag marrow">MarrowAI Workstation</span>
            </div>
            Welcome to MarrowAI Workstation. I am your autonomous, local Linux operating partner. Ask any question, dispatch automation plans, or manage isolated environments.
          </div>
        </div>

        <div class="input-row">
          <input type="text" id="prompt-input" placeholder="Type a command or question (e.g. 'launch arch vm', 'what is arch linux')..." onkeydown="handleKey(event)" />
          <button class="btn-icon" id="mic-btn" onclick="toggleMic()" title="Voice Input">
            <svg style="width:16px; height:16px;" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z"/></svg>
          </button>
          <button class="btn-icon" id="auto-listen-btn" onclick="toggleAutoListen()" title="Conversational Turn-Taking: Automatically listens after speaking answers">
            Auto-Listen: OFF
          </button>
          <button class="btn-primary" onclick="sendPrompt()">
            <span>Send</span>
            <svg style="width:14px; height:14px;" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 5l7 7m0 0l-7 7m7-7H3"/></svg>
          </button>
        </div>
      </div>

      <div class="card model-hub">
        <div class="card-title">
          <span>Offline Model Manager</span>
          <span class="prog-pct" id="prog-pct">0.0%</span>
        </div>

        <div style="display:flex; gap:10px; align-items:center;">
          <input type="text" id="custom-model-input" placeholder="Enter model tag (e.g. llama3.2, qwen2.5:3b, deepseek-r1:7b)..." style="flex:1;" />
          <select class="select-box" id="model-select" style="max-width:260px;" onchange="onModelSelectChange()">
            <option value="">-- Select or Download Model --</option>
          </select>
          <button class="btn-primary" id="btn-pull" onclick="downloadModel()">
            <svg style="width:14px; height:14px;" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"/></svg>
            Pull Model
          </button>
        </div>

        <div class="progress-bar-bg">
          <div class="progress-fill" id="progress-fill"></div>
        </div>
        <div class="prog-metrics">
          <span id="prog-detail">Ready to pull offline model into local Ollama</span>
          <span id="prog-bytes">[ 0 MB / 0 MB ]</span>
        </div>

        <div style="margin-top: 10px; border-top: 1px solid var(--card-border); padding-top: 12px;">
          <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
            <span style="font-size:0.75rem; font-weight:700; color:var(--text-muted); text-transform:uppercase; letter-spacing:0.8px;">Downloaded Models</span>
            <span id="installed-count" style="font-size:0.75rem; color:var(--text-dim);">Checking...</span>
          </div>
          <div id="installed-models-list" style="display:flex; flex-direction:column; gap:8px; max-height:160px; overflow-y:auto; padding-right:4px;">
            <div style="font-size:0.83rem; color:var(--text-dim); font-style:italic;">Querying local Ollama models...</div>
          </div>
        </div>
      </div>
    </div>
  </main>

  <script>
    let activeVoice = 'indian_female';
    let recognition = null;
    let isRecording = false;
    let autoListenActive = false;
    let currentAudio = null;
    let cachedLocalModels = [];
    let currentActiveModel = '';

    const PRESET_CATALOG = [
      { name: 'llama3.2', desc: 'llama3.2 (3.2B)' },
      { name: 'llama3.2:1b', desc: 'llama3.2:1b (1.3B)' },
      { name: 'qwen2.5-coder:14b', desc: 'qwen2.5-coder:14b' },
      { name: 'qwen2.5:3b', desc: 'qwen2.5:3b (1.9B)' },
      { name: 'mistral', desc: 'mistral (7B)' },
      { name: 'phi3', desc: 'phi3 (3.8B)' },
      { name: 'deepseek-r1:7b', desc: 'deepseek-r1:7b (4.7B)' }
    ];

    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      const SpeechRec = window.SpeechRecognition || window.webkitSpeechRecognition;
      recognition = new SpeechRec();
      recognition.continuous = false;
      recognition.interimResults = false;
      recognition.lang = 'en-IN';

      recognition.onresult = (e) => {
        const transcript = e.results[0][0].transcript;
        document.getElementById('prompt-input').value = transcript;
        toggleMic(false);
        sendPrompt();
      };
      recognition.onerror = () => toggleMic(false);
      recognition.onend = () => toggleMic(false);
    }

    if ('speechSynthesis' in window) {
      window.speechSynthesis.onvoiceschanged = () => {
        window.speechSynthesis.getVoices();
      };
    }

    function toggleAutoListen() {
      autoListenActive = !autoListenActive;
      const btn = document.getElementById('auto-listen-btn');
      if (autoListenActive) {
        btn.innerText = 'Auto-Listen: ON';
        btn.style.background = 'rgba(16, 185, 129, 0.15)';
        btn.style.borderColor = 'var(--status-green)';
        btn.style.color = 'var(--status-green)';
        toggleMic(true);
      } else {
        btn.innerText = 'Auto-Listen: OFF';
        btn.style.background = 'rgba(255, 255, 255, 0.04)';
        btn.style.borderColor = 'var(--card-border)';
        btn.style.color = '#fff';
        toggleMic(false);
      }
    }

    function toggleMic(forceState) {
      const btn = document.getElementById('mic-btn');
      if (forceState === false || (isRecording && forceState !== true)) {
        isRecording = false;
        btn.classList.remove('recording');
        if (recognition) {
          try { recognition.stop(); } catch(e){}
        }
      } else {
        if (!recognition) {
          alert('Speech recognition is supported in modern Chrome and Edge browsers.');
          return;
        }
        isRecording = true;
        btn.classList.add('recording');
        try {
          recognition.start();
        } catch(e) {}
      }
    }

    function setWaveActive(active) {
      const wave = document.getElementById('voice-wave');
      if (wave) {
        if (active) wave.classList.add('active');
        else wave.classList.remove('active');
      }
    }

    // Natural High-Fidelity Voice Synthesis:
    function speakAloud(text) {
      if (!text || !text.trim()) return;
      const clean = text.replace(/[*#`_]/g, '').trim().substring(0, 700);

      if (currentAudio) {
        try { currentAudio.pause(); } catch(e) {}
        currentAudio = null;
      }
      if ('speechSynthesis' in window) {
        window.speechSynthesis.cancel();
      }

      setWaveActive(true);

      const onPlaybackFinished = () => {
        currentAudio = null;
        setWaveActive(false);
        if (autoListenActive) {
          setTimeout(() => toggleMic(true), 400);
        }
      };

      const url = `/api/tts?voice=${encodeURIComponent(activeVoice)}&text=${encodeURIComponent(clean)}`;
      const audio = new Audio(url);
      currentAudio = audio;

      audio.onended = onPlaybackFinished;
      audio.onerror = () => {
        speakAloudWebSpeech(clean, onPlaybackFinished);
      };

      audio.play().catch(() => {
        speakAloudWebSpeech(clean, onPlaybackFinished);
      });
    }

    function speakAloudWebSpeech(text, onComplete = null) {
      if (!('speechSynthesis' in window)) {
        if (onComplete) onComplete();
        return;
      }
      window.speechSynthesis.cancel();
      const utter = new SpeechSynthesisUtterance(text);
      const voices = window.speechSynthesis.getVoices();
      const isFemale = activeVoice.includes('female');

      // Prioritize natural neural voices:
      let match = voices.find(v => (v.name.includes('Natural') || v.name.includes('Neural') || v.name.includes('Online')) && (v.lang.includes('en-IN') || v.name.includes('India')));
      if (!match) {
        match = voices.find(v => (v.name.includes('Natural') || v.name.includes('Neural') || v.name.includes('Online') || v.name.includes('Google')) && v.lang.startsWith('en'));
      }
      if (!match) {
        match = voices.find(v => v.lang.includes('en-IN') || v.lang.includes('hi-IN'));
      }
      if (!match) {
        match = voices.find(v => v.lang.startsWith('en'));
      }

      if (match) utter.voice = match;
      utter.rate = isFemale ? 0.98 : 0.95;
      utter.pitch = isFemale ? 1.02 : 0.96;

      utter.onend = () => {
        setWaveActive(false);
        if (onComplete) onComplete();
      };
      utter.onerror = () => {
        setWaveActive(false);
        if (onComplete) onComplete();
      };

      setWaveActive(true);
      window.speechSynthesis.speak(utter);
    }

    function changeVoice() {
      activeVoice = document.getElementById('voice-select').value;
    }

    function testVoice() {
      speakAloud("Namaste. I am MarrowAI, your offline Linux operating assistant. All systems are operational.");
    }

    function appendChat(role, text, tag = '', planSteps = null) {
      const box = document.getElementById('chat-box');
      const bubble = document.createElement('div');
      bubble.className = `chat-bubble ${role}`;
      let content = text ? formatMarkdown(text) : '';
      if (role === 'user') {
        bubble.innerHTML = `<div class="bubble-header"><span class="badge-tag user">You</span></div>` + content;
      } else if (role === 'narration') {
        bubble.innerHTML = content;
      } else {
        let planHtml = '';
        if (planSteps && planSteps.length > 0) {
          planHtml = `
            <div style="margin: 8px 0; background: rgba(99, 102, 241, 0.08); border: 1px solid rgba(99, 102, 241, 0.25); border-radius: 10px; padding: 10px 14px;">
              <div style="font-size:0.75rem; font-weight:700; color:#818cf8; text-transform:uppercase; letter-spacing:0.5px; margin-bottom:6px;">
                Plan Formulated:
              </div>
          `;
          planSteps.forEach((s, idx) => {
            planHtml += `
              <div style="font-size:0.83rem; color:#cbd5e1; margin-bottom:4px; display:flex; gap:8px;">
                <span style="color:#818cf8; font-weight:600;">${idx + 1}.</span>
                <span>${s.description || s.action_type}</span>
              </div>
            `;
          });
          planHtml += `</div>`;
        }
        bubble.innerHTML = `<div class="bubble-header"><span class="badge-tag marrow">MarrowAI ${tag ? '[' + tag + ']' : ''}</span></div>` + planHtml + content;
      }
      box.appendChild(bubble);
      box.scrollTop = box.scrollHeight;
    }

    function formatMarkdown(str) {
      if (!str) return '';
      let s = str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
      s = s.replace(/```([a-z]*)\n([\s\S]*?)```/g, (match, lang, code) => {
        const id = 'code-' + Math.random().toString(36).substr(2, 9);
        return `<div class="code-block"><button class="copy-code-btn" onclick="copyCode('${id}')">Copy</button><code id="${id}">${code.trim()}</code></div>`;
      });
      s = s.replace(/`([^`]+)`/g, '<code style="background:rgba(255,255,255,0.08); padding:2px 6px; border-radius:4px; font-family:JetBrains Mono,monospace; font-size:0.85em;">$1</code>');
      s = s.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
      s = s.replace(/\n/g, '<br>');
      return s;
    }

    function copyCode(id) {
      const el = document.getElementById(id);
      if (el) {
        navigator.clipboard.writeText(el.innerText).then(() => {
          alert('Code copied to clipboard.');
        });
      }
    }

    function handleKey(e) {
      if (e.key === 'Enter') sendPrompt();
    }

    function sendQuick(text) {
      document.getElementById('prompt-input').value = text;
      sendPrompt();
    }

    function appendConfirmationCard(data) {
      const box = document.getElementById('chat-box');
      const card = document.createElement('div');
      card.className = 'chat-bubble marrow';
      card.style.borderColor = 'rgba(245, 158, 11, 0.4)';
      card.style.background = 'rgba(245, 158, 11, 0.08)';
      card.id = 'active-confirmation-card';

      card.innerHTML = `
        <div class="bubble-header">
          <span class="badge-tag" style="color: var(--status-amber);">Authorization Required</span>
        </div>
        <div style="margin: 8px 0; font-size: 0.88rem;">${data.output || 'This action requires confirmation to execute.'}</div>
        <div style="display:flex; gap:10px; align-items:center; flex-wrap:wrap; margin-top:10px;">
          <input type="password" id="confirm-pwd-input" placeholder="Password (if sudo needed)" style="max-width:200px; padding:7px 12px; font-size:0.82rem;" />
          <button class="btn-primary" style="background:linear-gradient(135deg, #10b981, #059669); padding:7px 16px; font-size:0.83rem;" onclick="confirmAction(true)">Approve & Execute</button>
          <button class="btn-icon" style="padding:7px 14px; font-size:0.83rem;" onclick="confirmAction(false)">Cancel</button>
        </div>
      `;
      box.appendChild(card);
      box.scrollTop = box.scrollHeight;
    }

    async function confirmAction(proceed) {
      const card = document.getElementById('active-confirmation-card');
      const pwdInput = document.getElementById('confirm-pwd-input');
      const pwd = pwdInput ? pwdInput.value : '';
      if (card) card.remove();

      if (!proceed) {
        appendChat('marrow', 'Task execution cancelled by user.', 'CANCELLED');
        speakAloud('Task execution was cancelled.');
        return;
      }

      appendChat('user', 'Confirmed: Proceed with task execution');
      try {
        const resp = await fetch('/api/chat', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ prompt: 'yes', confirmed: true, password: pwd, voice_profile: activeVoice })
        });
        const data = await resp.json();
        if (data.output) {
          appendChat('marrow', data.output, data.status);
          speakAloud((data.narration ? data.narration + '. ' : '') + data.output.split('\n')[0]);
        } else {
          appendChat('marrow', data.status, data.status);
          speakAloud(`Task status: ${data.status}`);
        }
      } catch (err) {
        appendChat('marrow', 'Error confirming task: ' + err.message, 'ERROR');
      }
    }

    async function sendPrompt() {
      const input = document.getElementById('prompt-input');
      const text = input.value.trim();
      if (!text) return;
      input.value = '';
      appendChat('user', text);

      const activeCard = document.getElementById('active-confirmation-card');
      const lowered = text.toLowerCase();
      if (activeCard && ['yes', 'y', 'confirm', 'proceed', 'approve'].includes(lowered)) {
        confirmAction(true);
        return;
      }
      if (activeCard && ['no', 'n', 'cancel', 'abort', 'stop'].includes(lowered)) {
        confirmAction(false);
        return;
      }

      try {
        const resp = await fetch('/api/chat', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ prompt: text, voice_profile: activeVoice })
        });
        const data = await resp.json();

        if (data.status === 'requires_confirmation') {
          appendConfirmationCard(data);
          speakAloud("This high-risk action requires confirmation. Please approve or cancel.");
          return;
        }

        const conversationalIntents = [
          'explain_arch_linux', 'explain_ubuntu', 'explain_vm', 'explain_models',
          'voice_info', 'assistant_info', 'greeting', 'general_question', 'answer_question'
        ];
        const isConversational = conversationalIntents.includes(data.intent);

        let spokenText = '';
        if (isConversational) {
          const answer = data.output || data.narration || 'I am here to help you.';
          appendChat('marrow', answer, 'Answer');
          spokenText = answer;
        } else {
          if (data.narration) {
            appendChat('narration', data.narration);
          }
          if (data.output) {
            appendChat('marrow', data.output, data.status, data.plan_steps);
            spokenText = (data.narration ? data.narration + '. ' : '') + data.output.split('\n')[0];
          } else if (data.narration) {
            appendChat('marrow', data.narration, data.status, data.plan_steps);
            spokenText = data.narration;
          } else {
            appendChat('marrow', data.status, data.status, data.plan_steps);
            spokenText = `Status: ${data.status}`;
          }
        }

        if (spokenText) {
          speakAloud(spokenText);
        }
      } catch (err) {
        appendChat('marrow', 'Network or server error: ' + err.message, 'ERROR');
      }
    }

    function onModelSelectChange() {
      const sel = document.getElementById('model-select');
      const val = sel.value;
      if (!val) return;

      const installed = cachedLocalModels.find(m => m.name === val || val.startsWith(m.name));
      if (installed) {
        setActiveModel(installed.name);
      } else {
        document.getElementById('custom-model-input').value = val;
      }
    }

    async function downloadModel() {
      const input = document.getElementById('custom-model-input');
      const sel = document.getElementById('model-select');
      const model = (input.value || sel.value || 'llama3.2').trim();
      if (!model) return;
      const btn = document.getElementById('btn-pull');
      btn.disabled = true;
      btn.innerHTML = 'Pulling...';

      appendChat('narration', `Starting download of model '${model}'...`);
      speakAloud(`Starting download of model ${model}.`);

      const evtSource = new EventSource('/api/pull_stream?model=' + encodeURIComponent(model));
      evtSource.onmessage = (e) => {
        const data = JSON.parse(e.data);
        const pct = (data.percent || 0).toFixed(1);
        document.getElementById('prog-pct').innerText = pct + '%';
        document.getElementById('progress-fill').style.width = pct + '%';
        document.getElementById('prog-detail').innerText = data.detail || '';
        if (data.total > 0) {
          const cMb = (data.completed / (1024 * 1024)).toFixed(1);
          const tMb = (data.total / (1024 * 1024)).toFixed(1);
          document.getElementById('prog-bytes').innerText = `[ ${cMb} MB / ${tMb} MB ]`;
        }
        if (data.spoken) {
          speakAloud(data.spoken);
        }
        if (data.done) {
          evtSource.close();
          btn.disabled = false;
          btn.innerHTML = `<svg style="width:14px; height:14px;" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"/></svg> Pull Model`;
          appendChat('marrow', `Model '${model}' successfully downloaded and verified offline.`, 'SUCCESS');
          speakAloud(`Model ${model} download complete.`);
          refreshModels();
        }
        if (data.error) {
          evtSource.close();
          btn.disabled = false;
          btn.innerHTML = `<svg style="width:14px; height:14px;" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"/></svg> Pull Model`;
          appendChat('marrow', `Download failed: ${data.error}`, 'ERROR');
          speakAloud(`Model download failed.`);
        }
      };
      evtSource.onerror = () => {
        btn.disabled = false;
        btn.innerHTML = `<svg style="width:14px; height:14px;" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"/></svg> Pull Model`;
        refreshModels();
      };
    }

    async function refreshModels() {
      try {
        const res = await fetch('/api/models');
        const d = await res.json();
        cachedLocalModels = d.models || [];
        currentActiveModel = d.active_model || '';

        const list = document.getElementById('installed-models-list');
        const countSpan = document.getElementById('installed-count');
        const selectBox = document.getElementById('model-select');
        const headerModel = document.getElementById('header-model-name');

        if (currentActiveModel) {
          headerModel.innerText = currentActiveModel;
        } else if (cachedLocalModels.length > 0) {
          headerModel.innerText = cachedLocalModels[0].name;
        } else {
          headerModel.innerText = 'No Model Active';
        }

        if (selectBox) {
          selectBox.innerHTML = '';
          const defaultOpt = document.createElement('option');
          defaultOpt.value = '';
          defaultOpt.innerText = '-- Select or Download Model --';
          selectBox.appendChild(defaultOpt);

          if (cachedLocalModels.length > 0) {
            const grpInstalled = document.createElement('optgroup');
            grpInstalled.label = '✓ Downloaded & Ready';
            cachedLocalModels.forEach(m => {
              const opt = document.createElement('option');
              opt.value = m.name;
              const isActive = m.name === currentActiveModel || (currentActiveModel && currentActiveModel.startsWith(m.name));
              opt.innerText = `✓ ${m.name} (${m.size_formatted || 'Ready'})${isActive ? ' • [ACTIVE]' : ''}`;
              if (isActive) opt.selected = true;
              grpInstalled.appendChild(opt);
            });
            selectBox.appendChild(grpInstalled);
          }

          const grpPresets = document.createElement('optgroup');
          grpPresets.label = 'Available to Download';
          PRESET_CATALOG.forEach(p => {
            const isInstalled = cachedLocalModels.some(m => m.name === p.name || m.name.startsWith(p.name + ':'));
            if (!isInstalled) {
              const opt = document.createElement('option');
              opt.value = p.name;
              opt.innerText = `⬇ ${p.desc}`;
              grpPresets.appendChild(opt);
            }
          });
          selectBox.appendChild(grpPresets);
        }

        if (list) {
          list.innerHTML = '';
          countSpan.innerText = `${cachedLocalModels.length} installed`;

          if (cachedLocalModels.length === 0) {
            list.innerHTML = `<div style="font-size:0.83rem; color:var(--text-dim); font-style:italic;">No models downloaded yet. Pull a model above.</div>`;
            return;
          }

          cachedLocalModels.forEach(m => {
            const isActive = m.name === currentActiveModel || (currentActiveModel && currentActiveModel.startsWith(m.name));
            const card = document.createElement('div');
            card.className = 'model-card-item';
            card.innerHTML = `
              <div style="display:flex; flex-direction:column; gap:2px;">
                <div style="display:flex; align-items:center; gap:8px;">
                  <span style="font-weight:600; color:#fff; font-family:'JetBrains Mono',monospace;">${m.name}</span>
                  <span style="font-size:0.72rem; color:var(--text-muted); font-weight:600;">${m.size_formatted}</span>
                  ${isActive ? '<span class="pill green" style="padding:2px 8px; font-size:0.65rem;"><span class="dot"></span> ACTIVE</span>' : ''}
                </div>
                <div style="font-size:0.72rem; color:var(--text-dim);">
                  ${m.parameter_size ? 'Params: ' + m.parameter_size + ' | ' : ''}${m.quantization ? 'Quant: ' + m.quantization : ''}
                </div>
              </div>
              <div style="display:flex; gap:6px;">
                ${!isActive ? `<button class="action-btn" style="margin:0; padding:4px 10px; font-size:0.75rem;" onclick="setActiveModel('${m.name}')">Set Active</button>` : ''}
                <button class="btn-icon" style="padding:4px 8px; font-size:0.8rem;" title="Delete model" onclick="deleteModel('${m.name}')">🗑️</button>
              </div>
            `;
            list.appendChild(card);
          });
        }
      } catch(e) {}
    }

    async function setActiveModel(name) {
      try {
        const res = await fetch('/api/models/active', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ model: name })
        });
        const d = await res.json();
        if (d.success) {
          appendChat('marrow', `Active model set to '${name}'.`, 'CONFIG');
          speakAloud(`Active model set to ${name}.`);
          refreshModels();
        }
      } catch(e) {}
    }

    async function deleteModel(name) {
      if (!confirm(`Are you sure you want to delete model '${name}' from disk?`)) return;
      try {
        const res = await fetch('/api/models/delete', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ model: name })
        });
        const d = await res.json();
        if (d.success) {
          appendChat('marrow', `Model '${name}' deleted.`, 'CONFIG');
          speakAloud(`Model ${name} deleted.`);
          refreshModels();
        } else {
          alert('Failed to delete model: ' + d.message);
        }
      } catch(e) {}
    }

    function changeVoice() {
      activeVoice = document.getElementById('voice-select').value;
      const voiceLabels = {
        'indian_female': 'Indian English (Female - Neerja)',
        'indian_male': 'Indian English (Male - Prabhat)',
        'hindi_female': 'Hindi / Indian (Female - Swara)',
        'hindi_male': 'Hindi / Indian (Male - Madhur)'
      };
      const label = voiceLabels[activeVoice] || 'Indian Natural';
      const voiceText = document.getElementById('voice-status-text');
      if (voiceText) voiceText.innerText = label;
      speakAloud(`Voice switched to ${label}.`);
    }

    function testVoice() {
      speakAloud('Namaste. I am MarrowAI, your offline-first Linux operating assistant.');
    }

    async function refreshStatus() {
      try {
        const res = await fetch('/api/status');
        const d = await res.json();
        document.getElementById('val-cpu').innerText = `${d.cpu_load.toFixed(2)}`;
        document.getElementById('val-mem').innerText = `${d.ram_free_mb} MB`;
        document.getElementById('val-hyp').innerText = d.hypervisor;
        document.getElementById('pill-ollama').innerHTML = `<span class="dot"></span> Ollama: ${d.ollama_online ? 'ONLINE' : 'OFFLINE'}`;
        document.getElementById('pill-ollama').className = d.ollama_online ? 'pill green' : 'pill';
      } catch {}
    }

    setInterval(refreshStatus, 4000);
    setInterval(refreshModels, 8000);
    refreshStatus();
    refreshModels();
  </script>
</body>
</html>
"""


class MarrowWebHandler(BaseHTTPRequestHandler):
    assistant = MarrowAssistant()
    model_manager = OfflineModelManager()
    governor = ResourceGovernor()
    voice_engine = OfflineVoiceEngine()

    def do_GET(self) -> None:
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == "/":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(HTML_PAGE.encode("utf-8"))
            return

        if parsed.path == "/api/tts":
            qs = urllib.parse.parse_qs(parsed.query)
            text = qs.get("text", [""])[0]
            voice_prof = qs.get("voice", ["indian_female"])[0]
            if not text.strip():
                self.send_response(400)
                self.end_headers()
                return

            audio_data = self.voice_engine.synthesize_neural_audio(text, voice_prof)
            if audio_data:
                self.send_response(200)
                self.send_header("Content-Type", "audio/mpeg")
                self.send_header("Content-Length", str(len(audio_data)))
                self.send_header("Cache-Control", "public, max-age=3600")
                self.end_headers()
                self.wfile.write(audio_data)
                return

            # Fall back to offline WAV synthesis (espeak-ng / espeak / SAPI)
            wav_data = self.voice_engine.synthesize_offline_wav(text, voice_prof)
            if wav_data:
                self.send_response(200)
                self.send_header("Content-Type", "audio/wav")
                self.send_header("Content-Length", str(len(wav_data)))
                self.send_header("Cache-Control", "public, max-age=3600")
                self.end_headers()
                self.wfile.write(wav_data)
                return

            self.send_response(404)
            self.end_headers()
            return

        if parsed.path == "/api/status":
            from .vm_manager import VMManager
            mgr = VMManager()
            hyp = mgr.detect_hypervisors()
            tel = self.governor.get_telemetry()
            load1 = tel.load_average[0] if tel.load_average else 0.0
            data = {
                "cpu_load": load1,
                "ram_free_mb": tel.memory_available_mb,
                "ollama_online": self.model_manager.is_available(),
                "hypervisor": hyp.get("recommended", "QEMU/KVM"),
            }
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(data).encode("utf-8"))
            return

        if parsed.path == "/api/models":
            models = self.model_manager.list_local_models_detailed()
            active_model = getattr(self.assistant.model_provider, "model", "")
            data = {
                "models": models,
                "active_model": active_model,
                "ollama_online": self.model_manager.is_available(),
            }
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(data).encode("utf-8"))
            return

        if parsed.path == "/api/pull_stream":
            qs = urllib.parse.parse_qs(parsed.query)
            model_name = qs.get("model", ["llama3.2"])[0]

            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream")
            self.send_header("Cache-Control", "no-cache")
            self.send_header("Connection", "keep-alive")
            self.end_headers()

            milestones = {25: False, 50: False, 75: False}

            def on_progress(pct: float, detail: str, comp: int, tot: int) -> None:
                spoken = None
                for m in [25, 50, 75]:
                    if pct >= m and not milestones[m]:
                        milestones[m] = True
                        spoken = f"Model download is {m} percent complete."
                payload = {
                    "percent": pct,
                    "detail": detail,
                    "completed": comp,
                    "total": tot,
                    "done": False,
                    "spoken": spoken,
                }
                try:
                    self.wfile.write(f"data: {json.dumps(payload)}\n\n".encode("utf-8"))
                    self.wfile.flush()
                except Exception:
                    pass

            success, msg = self.model_manager.download_model(
                model_name,
                progress_callback=on_progress,
                voice_notify=False,
            )
            final_payload = {
                "percent": 100.0 if success else 0.0,
                "detail": msg,
                "completed": 1,
                "total": 1,
                "done": success,
                "error": None if success else msg,
                "spoken": f"Model {model_name} is downloaded and ready." if success else "Model download failed.",
            }
            try:
                self.wfile.write(f"data: {json.dumps(final_payload)}\n\n".encode("utf-8"))
                self.wfile.flush()
            except Exception:
                pass
            return

        self.send_response(404)
        self.end_headers()

    def do_POST(self) -> None:
        if self.path == "/api/chat":
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length).decode("utf-8")
            data = json.loads(body)
            prompt = data.get("prompt", "")
            confirmed = bool(data.get("confirmed", False))
            password = data.get("password")

            result = self.assistant.process(prompt, confirmed=confirmed, password=password)
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(result).encode("utf-8"))
            return

        if self.path == "/api/models/active":
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length).decode("utf-8")
            data = json.loads(body)
            model_name = str(data.get("model", "")).strip()
            if hasattr(self.assistant.model_provider, "model") and model_name:
                self.assistant.model_provider.model = model_name
                self.assistant.model_provider.configured_model = model_name
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"success": True, "active_model": model_name}).encode("utf-8"))
            return

        if self.path == "/api/models/delete":
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length).decode("utf-8")
            data = json.loads(body)
            model_name = str(data.get("model", "")).strip()
            ok, msg = self.model_manager.delete_model(model_name)
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"success": ok, "message": msg}).encode("utf-8"))
            return

        self.send_response(404)
        self.end_headers()

    def log_message(self, format: str, *args: Any) -> None:
        pass  # Suppress console log spam


def run_web_dashboard(port: int = 8765, open_browser: bool = True) -> None:
    server = ThreadingHTTPServer(("127.0.0.1", port), MarrowWebHandler)
    url = f"http://127.0.0.1:{port}"
    print(f"⚡ MarrowAI Web Workstation running at: {url}")
    print("Press Ctrl+C to stop.")
    if open_browser:
        threading.Thread(target=lambda: webbrowser.open(url), daemon=True).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\\nWeb Workstation stopped.")


if __name__ == "__main__":
    run_web_dashboard()
