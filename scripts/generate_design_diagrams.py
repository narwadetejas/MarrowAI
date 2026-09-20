#!/usr/bin/env python3
"""
MarrowAI System Design Image & Documentation Generator
Generates High-Level Design (HLD) and Low-Level Design (LLD) architectural diagrams
in both SVG and high-resolution PNG image formats into the docs/ directory.
"""
from __future__ import annotations

import os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont


DOCS_DIR = Path(r"c:\Users\tejas\Projects\MarrowAI\docs")
DOCS_DIR.mkdir(parents=True, exist_ok=True)


def build_hld_svg() -> str:
    return """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1600 2150" width="1600" height="2150" style="background:#090C15; font-family:'Plus Jakarta Sans',-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,sans-serif;">
  <defs>
    <!-- Gradients -->
    <linearGradient id="bgGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#090C15"/>
      <stop offset="50%" stop-color="#0E1424"/>
      <stop offset="100%" stop-color="#080A10"/>
    </linearGradient>
    <linearGradient id="headerGrad" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#6366F1"/>
      <stop offset="50%" stop-color="#8B5CF6"/>
      <stop offset="100%" stop-color="#38BDF8"/>
    </linearGradient>
    <linearGradient id="cardGrad" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#141C30" stop-opacity="0.9"/>
      <stop offset="100%" stop-color="#0E1424" stop-opacity="0.9"/>
    </linearGradient>
    <linearGradient id="accentCyan" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#06B6D4"/>
      <stop offset="100%" stop-color="#3B82F6"/>
    </linearGradient>
    <linearGradient id="accentGreen" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#10B981"/>
      <stop offset="100%" stop-color="#059669"/>
    </linearGradient>
    <linearGradient id="accentAmber" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#F59E0B"/>
      <stop offset="100%" stop-color="#D97706"/>
    </linearGradient>
    <linearGradient id="accentPurple" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#8B5CF6"/>
      <stop offset="100%" stop-color="#6366F1"/>
    </linearGradient>

    <!-- Filters -->
    <filter id="dropShadow" x="-10%" y="-10%" width="120%" height="125%">
      <feDropShadow dx="0" dy="8" stdDeviation="12" flood-color="#000" flood-opacity="0.45"/>
    </filter>
    <filter id="glowIndigo" x="-20%" y="-20%" width="140%" height="140%">
      <feGaussianBlur stdDeviation="8" result="blur" />
      <feComposite in="SourceGraphic" in2="blur" operator="over" />
    </filter>

    <!-- Arrow Marker -->
    <marker id="arrow" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1 L 10 5 L 0 9 z" fill="#6366F1"/>
    </marker>
    <marker id="arrowCyan" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1 L 10 5 L 0 9 z" fill="#38BDF8"/>
    </marker>
    <marker id="arrowGreen" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1 L 10 5 L 0 9 z" fill="#10B981"/>
    </marker>
    <marker id="arrowAmber" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1 L 10 5 L 0 9 z" fill="#F59E0B"/>
    </marker>
  </defs>

  <!-- Background -->
  <rect width="1600" height="2150" fill="url(#bgGrad)"/>
  <circle cx="200" cy="150" r="300" fill="#6366F1" opacity="0.04" filter="blur(60px)"/>
  <circle cx="1400" cy="900" r="400" fill="#38BDF8" opacity="0.03" filter="blur(80px)"/>
  <circle cx="300" cy="1700" r="350" fill="#8B5CF6" opacity="0.04" filter="blur(70px)"/>

  <!-- ==================== HEADER BLOCK ==================== -->
  <g transform="translate(80, 50)">
    <rect width="1440" height="110" rx="16" fill="#111728" stroke="#222F4C" stroke-width="1.5" filter="url(#dropShadow)"/>
    <rect x="2" y="2" width="6" height="106" rx="3" fill="url(#headerGrad)"/>
    
    <text x="36" y="44" font-size="26" font-weight="800" fill="#FFFFFF" letter-spacing="-0.5">MarrowAI — High-Level Architecture (HLD)</text>
    <text x="36" y="74" font-size="14" font-weight="500" fill="#94A3B8">Autonomous, Local-First Linux Workstation Assistant | System Topology &amp; Component Pipeline</text>
    
    <g transform="translate(1080, 28)">
      <rect width="105" height="28" rx="14" fill="#1E293B" stroke="#334155" stroke-width="1"/>
      <circle cx="14" cy="14" r="4" fill="#10B981"/>
      <text x="26" y="19" font-size="11" font-weight="700" fill="#E2E8F0">LOCAL-FIRST</text>
      
      <rect x="118" y="0" width="105" height="28" rx="14" fill="#1E293B" stroke="#334155" stroke-width="1"/>
      <circle cx="132" cy="14" r="4" fill="#6366F1"/>
      <text x="144" y="19" font-size="11" font-weight="700" fill="#E2E8F0">ZERO-TRUST</text>

      <rect x="236" y="0" width="85" height="28" rx="14" fill="#1E293B" stroke="#334155" stroke-width="1"/>
      <circle cx="250" cy="14" r="4" fill="#38BDF8"/>
      <text x="262" y="19" font-size="11" font-weight="700" fill="#E2E8F0">v0.2.0</text>
    </g>
  </g>

  <!-- ==================== LAYER 1: CLIENT & PRESENTATION LAYER ==================== -->
  <g transform="translate(80, 190)">
    <rect width="1440" height="230" rx="16" fill="url(#cardGrad)" stroke="#1F2A44" stroke-width="1.5" filter="url(#dropShadow)"/>
    <path d="M 0 16 Q 0 0 16 0 L 1424 0 Q 1440 0 1440 16 L 1440 40 L 0 40 Z" fill="#172138"/>
    <text x="24" y="26" font-size="13" font-weight="800" fill="#38BDF8" letter-spacing="1">LAYER 1: USER CLIENT &amp; PRESENTATION INTERFACES</text>

    <!-- 1.1 Web Workstation -->
    <g transform="translate(24, 55)">
      <rect width="325" height="150" rx="12" fill="#0D1322" stroke="#253556" stroke-width="1.2"/>
      <text x="18" y="28" font-size="15" font-weight="700" fill="#FFFFFF">Web GUI Workstation</text>
      <text x="18" y="48" font-size="11" font-weight="600" fill="#6366F1">ThreadingHTTPServer (:8765)</text>
      <text x="18" y="72" font-size="11" fill="#94A3B8">• Dark Obsidian Frosted Glass UI</text>
      <text x="18" y="90" font-size="11" fill="#94A3B8">• Dynamic Model Selector (Installed/Ready)</text>
      <text x="18" y="108" font-size="11" fill="#94A3B8">• Server-Sent Events (/api/pull_stream)</text>
      <text x="18" y="126" font-size="11" fill="#94A3B8">• Speech Waveform &amp; Auto-Listen Loop</text>
    </g>

    <!-- 1.2 Desktop GUI -->
    <g transform="translate(375, 55)">
      <rect width="325" height="150" rx="12" fill="#0D1322" stroke="#253556" stroke-width="1.2"/>
      <text x="18" y="28" font-size="15" font-weight="700" fill="#FFFFFF">Tkinter Desktop GUI</text>
      <text x="18" y="48" font-size="11" font-weight="600" fill="#38BDF8">MarrowAIWindow (Clam Engine)</text>
      <text x="18" y="72" font-size="11" fill="#94A3B8">• Real-time Telemetry &amp; System Meters</text>
      <text x="18" y="90" font-size="11" fill="#94A3B8">• Grouped Installed Combobox Selector</text>
      <text x="18" y="108" font-size="11" fill="#94A3B8">• Determinate Progressbar (0-100%)</text>
      <text x="18" y="126" font-size="11" fill="#94A3B8">• Security Audit Log Modal Viewer</text>
    </g>

    <!-- 1.3 CLI Suite -->
    <g transform="translate(725, 55)">
      <rect width="325" height="150" rx="12" fill="#0D1322" stroke="#253556" stroke-width="1.2"/>
      <text x="18" y="28" font-size="15" font-weight="700" fill="#FFFFFF">CLI &amp; Interactive Shell</text>
      <text x="18" y="48" font-size="11" font-weight="600" fill="#10B981">marrowai / marrowai-chat</text>
      <text x="18" y="72" font-size="11" fill="#94A3B8">• Interactive REPL with Safety Prompts</text>
      <text x="18" y="90" font-size="11" fill="#94A3B8">• Headless Batch &amp; Script Dispatch</text>
      <text x="18" y="108" font-size="11" fill="#94A3B8">• marrowai-doctor (Diagnostic Probe)</text>
      <text x="18" y="126" font-size="11" fill="#94A3B8">• marrowai-scaffold (Workspace Init)</text>
    </g>

    <!-- 1.4 Voice Interface -->
    <g transform="translate(1075, 55)">
      <rect width="340" height="150" rx="12" fill="#0D1322" stroke="#253556" stroke-width="1.2"/>
      <text x="18" y="28" font-size="15" font-weight="700" fill="#FFFFFF">Voice Ingest &amp; Natural Audio</text>
      <text x="18" y="48" font-size="11" font-weight="600" fill="#F59E0B">Web Speech + Neural Edge-TTS</text>
      <text x="18" y="72" font-size="11" fill="#94A3B8">• Web Speech Dictation (en-IN / hi-IN)</text>
      <text x="18" y="90" font-size="11" fill="#94A3B8">• Microsoft Neural TTS (Studio Quality)</text>
      <text x="18" y="108" font-size="11" fill="#94A3B8">• Conversational Turn-Taking (Auto-Listen)</text>
      <text x="18" y="126" font-size="11" fill="#94A3B8">• Sub-5ms In-Memory LRU Audio Cache</text>
    </g>
  </g>

  <!-- Connectors Layer 1 -> Layer 2 -->
  <line x1="800" y1="420" x2="800" y2="455" stroke="#6366F1" stroke-width="2.5" marker-end="url(#arrow)"/>
  <rect x="710" y="426" width="180" height="22" rx="6" fill="#1A233A" stroke="#374872" stroke-width="1"/>
  <text x="722" y="441" font-size="10.5" font-weight="700" fill="#C7D2FE">Typed UserInput Payload</text>

  <!-- ==================== LAYER 2: MULTIMODAL INGESTION & NORMALIZATION ==================== -->
  <g transform="translate(80, 460)">
    <rect width="1440" height="130" rx="16" fill="url(#cardGrad)" stroke="#1F2A44" stroke-width="1.5" filter="url(#dropShadow)"/>
    <path d="M 0 16 Q 0 0 16 0 L 1424 0 Q 1440 0 1440 16 L 1440 36 L 0 36 Z" fill="#172138"/>
    <text x="24" y="24" font-size="13" font-weight="800" fill="#38BDF8" letter-spacing="1">LAYER 2: MULTIMODAL INGESTION &amp; NORMALIZATION</text>

    <!-- STT -->
    <g transform="translate(24, 48)">
      <rect width="440" height="68" rx="8" fill="#0D1322" stroke="#22304E"/>
      <text x="16" y="28" font-size="13" font-weight="700" fill="#FFFFFF">Speech-To-Text (STT) Abstraction</text>
      <text x="16" y="48" font-size="11" fill="#94A3B8">Browser SpeechRec API | FFmpeg pipeline fallback | Audio chunk validation</text>
    </g>

    <!-- Normalizer -->
    <g transform="translate(488, 48)">
      <rect width="460" height="68" rx="8" fill="#0D1322" stroke="#22304E"/>
      <text x="16" y="28" font-size="13" font-weight="700" fill="#FFFFFF">Input Normalizer &amp; Intent Classifier</text>
      <text x="16" y="48" font-size="11" fill="#94A3B8">Sanitizes control tokens | Classifies intent (Conversational vs OS Execution)</text>
    </g>

    <!-- Context -->
    <g transform="translate(972, 48)">
      <rect width="440" height="68" rx="8" fill="#0D1322" stroke="#22304E"/>
      <text x="16" y="28" font-size="13" font-weight="700" fill="#FFFFFF">Context &amp; Session Memory Store</text>
      <text x="16" y="48" font-size="11" fill="#94A3B8">Session history | Active model selection | Security confirmation context</text>
    </g>
  </g>

  <!-- Connectors Layer 2 -> Layer 3 -->
  <line x1="800" y1="590" x2="800" y2="625" stroke="#6366F1" stroke-width="2.5" marker-end="url(#arrow)"/>
  <rect x="690" y="596" width="220" height="22" rx="6" fill="#1A233A" stroke="#374872" stroke-width="1"/>
  <text x="702" y="611" font-size="10.5" font-weight="700" fill="#C7D2FE">Sanitized Prompt + Session Context</text>

  <!-- ==================== LAYER 3: COGNITIVE & PLANNING ENGINE (LLM OUTSIDE PRIVILEGED PATH) ==================== -->
  <g transform="translate(80, 630)">
    <rect width="1440" height="260" rx="16" fill="url(#cardGrad)" stroke="#1F2A44" stroke-width="1.5" filter="url(#dropShadow)"/>
    <path d="M 0 16 Q 0 0 16 0 L 1424 0 Q 1440 0 1440 16 L 1440 40 L 0 40 Z" fill="#172138"/>
    <text x="24" y="26" font-size="13" font-weight="800" fill="#6366F1" letter-spacing="1">LAYER 3: COGNITIVE &amp; PLANNING ENGINE (LLM OUTSIDE PRIVILEGED PATH)</text>

    <!-- Assistant Facade -->
    <g transform="translate(24, 55)">
      <rect width="360" height="185" rx="12" fill="#0D1322" stroke="#253556" stroke-width="1.2"/>
      <text x="18" y="28" font-size="15" font-weight="700" fill="#FFFFFF">MarrowAssistant Facade</text>
      <text x="18" y="48" font-size="11" font-weight="600" fill="#6366F1">Core Orchestrator (assistant.py)</text>
      <text x="18" y="74" font-size="11" fill="#94A3B8">• Manages end-to-end request lifecycle</text>
      <text x="18" y="94" font-size="11" fill="#94A3B8">• Enforces deterministic planning dispatch</text>
      <text x="18" y="114" font-size="11" fill="#94A3B8">• Handles conversational vs task branches</text>
      <text x="18" y="134" font-size="11" fill="#94A3B8">• Intercepts interactive security confirmations</text>
      <text x="18" y="154" font-size="11" fill="#94A3B8">• Triggers voice narration &amp; UI responses</text>
    </g>

    <!-- Planner -->
    <g transform="translate(410, 55)">
      <rect width="340" height="185" rx="12" fill="#0D1322" stroke="#253556" stroke-width="1.2"/>
      <text x="18" y="28" font-size="15" font-weight="700" fill="#FFFFFF">Autonomous Planner</text>
      <text x="18" y="48" font-size="11" font-weight="600" fill="#38BDF8">Deterministic Task Decomposition</text>
      <text x="18" y="74" font-size="11" fill="#94A3B8">• Regex + Semantic intent recognition</text>
      <text x="18" y="94" font-size="11" fill="#94A3B8">• VM creation pipeline planning (Arch/Ubuntu)</text>
      <text x="18" y="114" font-size="11" fill="#94A3B8">• Project scaffolding &amp; test plan generation</text>
      <text x="18" y="134" font-size="11" fill="#94A3B8">• Model pull &amp; delete plan mapping</text>
      <text x="18" y="154" font-size="11" fill="#94A3B8">• Emits strictly typed TaskPlan data contract</text>
    </g>

    <!-- Model Provider -->
    <g transform="translate(775, 55)">
      <rect width="320" height="185" rx="12" fill="#0D1322" stroke="#253556" stroke-width="1.2"/>
      <text x="18" y="28" font-size="15" font-weight="700" fill="#FFFFFF">Model Provider Layer</text>
      <text x="18" y="48" font-size="11" font-weight="600" fill="#10B981">OllamaProvider / LocalModel</text>
      <text x="18" y="74" font-size="11" fill="#94A3B8">• Dynamic endpoint auto-discovery</text>
      <text x="18" y="94" font-size="11" fill="#94A3B8">• Connects to Ollama REST runtime</text>
      <text x="18" y="114" font-size="11" fill="#94A3B8">• JSON schema validation enforcement</text>
      <text x="18" y="134" font-size="11" fill="#94A3B8">• Fallback handling for offline runtimes</text>
      <text x="18" y="154" font-size="11" fill="#94A3B8">• Strictly separated from execution path</text>
    </g>

    <!-- Typed Contract Guard -->
    <g transform="translate(1120, 55)">
      <rect width="295" height="185" rx="12" fill="#0D1322" stroke="#F59E0B" stroke-width="1.2"/>
      <text x="18" y="28" font-size="15" font-weight="700" fill="#F59E0B">Typed Data Contracts</text>
      <text x="18" y="48" font-size="11" font-weight="600" fill="#CBD5E1">interfaces.py Validation Gate</text>
      <text x="18" y="74" font-size="11" fill="#94A3B8">• TaskPlan (id, intent, risk_level)</text>
      <text x="18" y="94" font-size="11" fill="#94A3B8">• PlanStep (tool_name, parameters)</text>
      <text x="18" y="114" font-size="11" fill="#94A3B8">• NO raw shell string emission</text>
      <text x="18" y="134" font-size="11" fill="#94A3B8">• Formal parameters validation</text>
      <text x="18" y="154" font-size="11" fill="#94A3B8">• Immutable plan representation</text>
    </g>
  </g>

  <!-- Connectors Layer 3 -> Layer 4 -->
  <line x1="800" y1="890" x2="800" y2="925" stroke="#F59E0B" stroke-width="2.5" marker-end="url(#arrowAmber)"/>
  <rect x="680" y="896" width="240" height="22" rx="6" fill="#1A233A" stroke="#374872" stroke-width="1"/>
  <text x="692" y="911" font-size="10.5" font-weight="700" fill="#FDE68A">TaskPlan (Unverified Candidate)</text>

  <!-- ==================== LAYER 4: SAFETY, SECURITY & GOVERNANCE GATEWAY ==================== -->
  <g transform="translate(80, 930)">
    <rect width="1440" height="230" rx="16" fill="url(#cardGrad)" stroke="#F59E0B" stroke-width="1.8" filter="url(#dropShadow)"/>
    <path d="M 0 16 Q 0 0 16 0 L 1424 0 Q 1440 0 1440 16 L 1440 40 L 0 40 Z" fill="#241B10"/>
    <text x="24" y="26" font-size="13" font-weight="800" fill="#F59E0B" letter-spacing="1">LAYER 4: ZERO-TRUST SAFETY, SECURITY &amp; GOVERNANCE GATEWAY</text>

    <!-- Risk Classifier -->
    <g transform="translate(24, 55)">
      <rect width="330" height="155" rx="12" fill="#0D1322" stroke="#253556" stroke-width="1.2"/>
      <text x="18" y="28" font-size="15" font-weight="700" fill="#FFFFFF">Risk Classifier</text>
      <text x="18" y="48" font-size="11" font-weight="600" fill="#38BDF8">Three-Tier Classification</text>
      <text x="18" y="74" font-size="11" fill="#10B981">🟢 LOW: Safe reads, telemetry, status queries</text>
      <text x="18" y="94" font-size="11" fill="#F59E0B">🟡 MEDIUM: File scaffolding, doc generation</text>
      <text x="18" y="114" font-size="11" fill="#EF4444">🔴 HIGH: Sudo, VM creation, deletion, packages</text>
      <text x="18" y="136" font-size="11" fill="#94A3B8">• Evaluates action_type, tool, and target args</text>
    </g>

    <!-- Policy Evaluator -->
    <g transform="translate(378, 55)">
      <rect width="330" height="155" rx="12" fill="#0D1322" stroke="#253556" stroke-width="1.2"/>
      <text x="18" y="28" font-size="15" font-weight="700" fill="#FFFFFF">Safety Policy Gate</text>
      <text x="18" y="48" font-size="11" font-weight="600" fill="#F59E0B">ALLOW / REVIEW / DENY</text>
      <text x="18" y="74" font-size="11" fill="#94A3B8">• Checks against strict policy rules</text>
      <text x="18" y="94" font-size="11" fill="#94A3B8">• Rejects prohibited commands (rm -rf /, etc.)</text>
      <text x="18" y="114" font-size="11" fill="#94A3B8">• Flags high-risk actions for user authorization</text>
      <text x="18" y="136" font-size="11" fill="#94A3B8">• Emits SafetyDecision data contract</text>
    </g>

    <!-- Confirmation Loop -->
    <g transform="translate(732, 55)">
      <rect width="340" height="155" rx="12" fill="#0D1322" stroke="#253556" stroke-width="1.2"/>
      <text x="18" y="28" font-size="15" font-weight="700" fill="#FFFFFF">User Authorization Gate</text>
      <text x="18" y="48" font-size="11" font-weight="600" fill="#EF4444">Interactive Security Confirmation</text>
      <text x="18" y="74" font-size="11" fill="#94A3B8">• Halts execution for all HIGH-risk actions</text>
      <text x="18" y="94" font-size="11" fill="#94A3B8">• Displays action details &amp; password prompt</text>
      <text x="18" y="114" font-size="11" fill="#94A3B8">• Requires explicit user approval ('yes'/button)</text>
      <text x="18" y="136" font-size="11" fill="#94A3B8">• Clean cancellation path without residue</text>
    </g>

    <!-- Audit Logger -->
    <g transform="translate(1096, 55)">
      <rect width="320" height="155" rx="12" fill="#0D1322" stroke="#253556" stroke-width="1.2"/>
      <text x="18" y="28" font-size="15" font-weight="700" fill="#FFFFFF">Security Audit Logger</text>
      <text x="18" y="48" font-size="11" font-weight="600" fill="#10B981">Append-Only Audit Trail</text>
      <text x="18" y="74" font-size="11" fill="#94A3B8">• Records timestamps, prompts, decisions</text>
      <text x="18" y="94" font-size="11" fill="#94A3B8">• Logs tool calls, exit codes, and outcomes</text>
      <text x="18" y="114" font-size="11" fill="#94A3B8">• Secret masking: passwords never logged</text>
      <text x="18" y="136" font-size="11" fill="#94A3B8">• Inspectable in GUI &amp; audit log file</text>
    </g>
  </g>

  <!-- Connectors Layer 4 -> Layer 5 -->
  <line x1="800" y1="1160" x2="800" y2="1195" stroke="#10B981" stroke-width="2.5" marker-end="url(#arrowGreen)"/>
  <rect x="670" y="1166" width="260" height="22" rx="6" fill="#1A233A" stroke="#374872" stroke-width="1"/>
  <text x="682" y="1181" font-size="10.5" font-weight="700" fill="#A7F3D0">Validated &amp; Approved ToolCalls</text>

  <!-- ==================== LAYER 5: TOOL ROUTING & ORCHESTRATION ENGINE ==================== -->
  <g transform="translate(80, 1200)">
    <rect width="1440" height="260" rx="16" fill="url(#cardGrad)" stroke="#1F2A44" stroke-width="1.5" filter="url(#dropShadow)"/>
    <path d="M 0 16 Q 0 0 16 0 L 1424 0 Q 1440 0 1440 16 L 1440 40 L 0 40 Z" fill="#172138"/>
    <text x="24" y="26" font-size="13" font-weight="800" fill="#10B981" letter-spacing="1">LAYER 5: TOOL ROUTING &amp; ORCHESTRATION ENGINE</text>

    <!-- Tool Router -->
    <g transform="translate(24, 55)">
      <rect width="260" height="185" rx="12" fill="#0D1322" stroke="#253556" stroke-width="1.2"/>
      <text x="18" y="28" font-size="15" font-weight="700" fill="#FFFFFF">Tool Router</text>
      <text x="18" y="48" font-size="11" font-weight="600" fill="#38BDF8">Schema Validation</text>
      <text x="18" y="74" font-size="11" fill="#94A3B8">• Tool registration map</text>
      <text x="18" y="94" font-size="11" fill="#94A3B8">• Argument type coercion</text>
      <text x="18" y="114" font-size="11" fill="#94A3B8">• Timeout enforcement</text>
      <text x="18" y="134" font-size="11" fill="#94A3B8">• Resource profile check</text>
      <text x="18" y="154" font-size="11" fill="#94A3B8">• Dispatches to executors</text>
    </g>

    <!-- Tool: VM Manager -->
    <g transform="translate(304, 55)">
      <rect width="265" height="185" rx="12" fill="#0D1322" stroke="#253556" stroke-width="1.2"/>
      <text x="18" y="28" font-size="15" font-weight="700" fill="#FFFFFF">VM Manager</text>
      <text x="18" y="48" font-size="11" font-weight="600" fill="#6366F1">Hypervisor Automation</text>
      <text x="18" y="74" font-size="11" fill="#94A3B8">• KVM / QEMU / VBox detect</text>
      <text x="18" y="94" font-size="11" fill="#94A3B8">• Automated ISO verification</text>
      <text x="18" y="114" font-size="11" fill="#94A3B8">• Unattended cloud-init setup</text>
      <text x="18" y="134" font-size="11" fill="#94A3B8">• Arch &amp; Ubuntu VM deploy</text>
      <text x="18" y="154" font-size="11" fill="#94A3B8">• SSH key &amp; network bridging</text>
    </g>

    <!-- Tool: Model Manager -->
    <g transform="translate(589, 55)">
      <rect width="265" height="185" rx="12" fill="#0D1322" stroke="#253556" stroke-width="1.2"/>
      <text x="18" y="28" font-size="15" font-weight="700" fill="#FFFFFF">ManageModelsTool</text>
      <text x="18" y="48" font-size="11" font-weight="600" fill="#F59E0B">Local Model Operations</text>
      <text x="18" y="74" font-size="11" fill="#94A3B8">• Pull / delete / list models</text>
      <text x="18" y="94" font-size="11" fill="#94A3B8">• Presets vs custom tags</text>
      <text x="18" y="114" font-size="11" fill="#94A3B8">• Progress streaming hook</text>
      <text x="18" y="134" font-size="11" fill="#94A3B8">• Active model switching</text>
      <text x="18" y="154" font-size="11" fill="#94A3B8">• Local storage inspection</text>
    </g>

    <!-- Tool: Scaffold & Diagnostics -->
    <g transform="translate(874, 55)">
      <rect width="265" height="185" rx="12" fill="#0D1322" stroke="#253556" stroke-width="1.2"/>
      <text x="18" y="28" font-size="15" font-weight="700" fill="#FFFFFF">Scaffold &amp; Diagnostics</text>
      <text x="18" y="48" font-size="11" font-weight="600" fill="#10B981">Workspace &amp; Health</text>
      <text x="18" y="74" font-size="11" fill="#94A3B8">• ProjectScaffold (FastAPI/Go)</text>
      <text x="18" y="94" font-size="11" fill="#94A3B8">• SystemDiagnosticsTool</text>
      <text x="18" y="114" font-size="11" fill="#94A3B8">• Disk, memory, load telemetry</text>
      <text x="18" y="134" font-size="11" fill="#94A3B8">• Test suite execution runner</text>
      <text x="18" y="154" font-size="11" fill="#94A3B8">• Workspace isolation checks</text>
    </g>

    <!-- Executor Engine -->
    <g transform="translate(1159, 55)">
      <rect width="255" height="185" rx="12" fill="#0D1322" stroke="#253556" stroke-width="1.2"/>
      <text x="18" y="28" font-size="15" font-weight="700" fill="#FFFFFF">Execution Engine</text>
      <text x="18" y="48" font-size="11" font-weight="600" fill="#38BDF8">executor.py Subprocess</text>
      <text x="18" y="74" font-size="11" fill="#94A3B8">• Bounded subprocess exec</text>
      <text x="18" y="94" font-size="11" fill="#94A3B8">• Non-zero exit code capture</text>
      <text x="18" y="114" font-size="11" fill="#94A3B8">• Sandboxed working dir</text>
      <text x="18" y="134" font-size="11" fill="#94A3B8">• GUI automation fallback</text>
      <text x="18" y="154" font-size="11" fill="#94A3B8">• Emits ExecutionResult</text>
    </g>
  </g>

  <!-- Connectors Layer 5 -> Layer 6 -->
  <line x1="800" y1="1460" x2="800" y2="1495" stroke="#38BDF8" stroke-width="2.5" marker-end="url(#arrowCyan)"/>
  <rect x="680" y="1466" width="240" height="22" rx="6" fill="#1A233A" stroke="#374872" stroke-width="1"/>
  <text x="692" y="1481" font-size="10.5" font-weight="700" fill="#BAE6FD">Subsystem Invocations &amp; Telemetry</text>

  <!-- ==================== LAYER 6: OFFLINE SUBSYSTEMS & PERSISTENCE ==================== -->
  <g transform="translate(80, 1500)">
    <rect width="1440" height="260" rx="16" fill="url(#cardGrad)" stroke="#1F2A44" stroke-width="1.5" filter="url(#dropShadow)"/>
    <path d="M 0 16 Q 0 0 16 0 L 1424 0 Q 1440 0 1440 16 L 1440 40 L 0 40 Z" fill="#172138"/>
    <text x="24" y="26" font-size="13" font-weight="800" fill="#38BDF8" letter-spacing="1">LAYER 6: OFFLINE SUBSYSTEMS, RESOURCE GOVERNOR &amp; PERSISTENCE</text>

    <!-- Offline Model Manager -->
    <g transform="translate(24, 55)">
      <rect width="330" height="185" rx="12" fill="#0D1322" stroke="#253556" stroke-width="1.2"/>
      <text x="18" y="28" font-size="15" font-weight="700" fill="#FFFFFF">Offline Model Manager</text>
      <text x="18" y="48" font-size="11" font-weight="600" fill="#6366F1">model_manager.py</text>
      <text x="18" y="74" font-size="11" fill="#94A3B8">• Ollama endpoint discovery (WSL/host)</text>
      <text x="18" y="94" font-size="11" fill="#94A3B8">• Streaming pull with milestones (25/50/75%)</text>
      <text x="18" y="114" font-size="11" fill="#94A3B8">• Local model inventory &amp; size inspection</text>
      <text x="18" y="134" font-size="11" fill="#94A3B8">• Auto-persistence across app reinstalls</text>
      <text x="18" y="154" font-size="11" fill="#94A3B8">• Disk storage: ~/.ollama/models</text>
    </g>

    <!-- Resource Governor -->
    <g transform="translate(378, 55)">
      <rect width="330" height="185" rx="12" fill="#0D1322" stroke="#253556" stroke-width="1.2"/>
      <text x="18" y="28" font-size="15" font-weight="700" fill="#FFFFFF">Resource Governor</text>
      <text x="18" y="48" font-size="11" font-weight="600" fill="#10B981">governor.py (Independent of LLM)</text>
      <text x="18" y="74" font-size="11" fill="#94A3B8">• Collects 1m/5m/15m CPU load telemetry</text>
      <text x="18" y="94" font-size="11" fill="#94A3B8">• Monitors free memory &amp; swap pressure</text>
      <text x="18" y="114" font-size="11" fill="#94A3B8">• Evaluates is_safe_to_execute() gate</text>
      <text x="18" y="134" font-size="11" fill="#94A3B8">• Graceful fallback without eBPF</text>
      <text x="18" y="154" font-size="11" fill="#94A3B8">• Prevents workstation resource lockup</text>
    </g>

    <!-- Natural Voice Engine -->
    <g transform="translate(732, 55)">
      <rect width="340" height="185" rx="12" fill="#0D1322" stroke="#253556" stroke-width="1.2"/>
      <text x="18" y="28" font-size="15" font-weight="700" fill="#FFFFFF">Offline Voice Engine</text>
      <text x="18" y="48" font-size="11" font-weight="600" fill="#F59E0B">voice_engine.py</text>
      <text x="18" y="74" font-size="11" fill="#94A3B8">• Microsoft Neural Edge-TTS (Primary)</text>
      <text x="18" y="94" font-size="11" fill="#94A3B8">• Windows SAPI / .NET Speech (Natural)</text>
      <text x="18" y="114" font-size="11" fill="#94A3B8">• espeak-ng / spd-say (Offline Linux)</text>
      <text x="18" y="134" font-size="11" fill="#94A3B8">• 256-entry in-memory LRU audio cache</text>
      <text x="18" y="154" font-size="11" fill="#94A3B8">• Native audio players: ffplay, mpv, SAPI</text>
    </g>

    <!-- Vector DB & Memory -->
    <g transform="translate(1096, 55)">
      <rect width="320" height="185" rx="12" fill="#0D1322" stroke="#253556" stroke-width="1.2"/>
      <text x="18" y="28" font-size="15" font-weight="700" fill="#FFFFFF">Vector Memory &amp; Storage</text>
      <text x="18" y="48" font-size="11" font-weight="600" fill="#38BDF8">vector_db.py</text>
      <text x="18" y="74" font-size="11" fill="#94A3B8">• SemanticEmbedder: 256-d dense vector</text>
      <text x="18" y="94" font-size="11" fill="#94A3B8">• Zero-dependency offline tokenization</text>
      <text x="18" y="114" font-size="11" fill="#94A3B8">• SQLite blob vector store + metadata</text>
      <text x="18" y="134" font-size="11" fill="#94A3B8">• Cosine similarity search for local RAG</text>
      <text x="18" y="154" font-size="11" fill="#94A3B8">• Fast retrieval for project contexts</text>
    </g>
  </g>

  <!-- Connectors Layer 6 -> Layer 7 -->
  <line x1="800" y1="1760" x2="800" y2="1795" stroke="#6366F1" stroke-width="2.5" marker-end="url(#arrow)"/>
  <rect x="690" y="1766" width="220" height="22" rx="6" fill="#1A233A" stroke="#374872" stroke-width="1"/>
  <text x="702" y="1781" font-size="10.5" font-weight="700" fill="#C7D2FE">Kernel / System Interfaces</text>

  <!-- ==================== LAYER 7: OS, KERNEL & HYPERVISOR BOUNDARY ==================== -->
  <g transform="translate(80, 1800)">
    <rect width="1440" height="250" rx="16" fill="url(#cardGrad)" stroke="#1F2A44" stroke-width="1.5" filter="url(#dropShadow)"/>
    <path d="M 0 16 Q 0 0 16 0 L 1424 0 Q 1440 0 1440 16 L 1440 40 L 0 40 Z" fill="#172138"/>
    <text x="24" y="26" font-size="13" font-weight="800" fill="#8B5CF6" letter-spacing="1">LAYER 7: OPERATING SYSTEM, KERNEL &amp; HYPERVISOR BOUNDARY</text>

    <!-- OS Runtimes -->
    <g transform="translate(24, 55)">
      <rect width="440" height="175" rx="12" fill="#0D1322" stroke="#253556" stroke-width="1.2"/>
      <text x="18" y="28" font-size="15" font-weight="700" fill="#FFFFFF">Operating System Runtimes</text>
      <text x="18" y="48" font-size="11" font-weight="600" fill="#38BDF8">Linux Desktop / WSL2 / Windows</text>
      <text x="18" y="74" font-size="11" fill="#94A3B8">• Debian / Ubuntu package distribution (marrowai.deb)</text>
      <text x="18" y="94" font-size="11" fill="#94A3B8">• WSL2 Linux environment with Windows host interop</text>
      <text x="18" y="114" font-size="11" fill="#94A3B8">• Arch Linux target execution runtime</text>
      <text x="18" y="134" font-size="11" fill="#94A3B8">• Multi-shell support: bash, sh, PowerShell</text>
      <text x="18" y="154" font-size="11" fill="#94A3B8">• Systemd service auto-enablement for Ollama</text>
    </g>

    <!-- Kernel & Proc -->
    <g transform="translate(488, 55)">
      <rect width="460" height="175" rx="12" fill="#0D1322" stroke="#253556" stroke-width="1.2"/>
      <text x="18" y="28" font-size="15" font-weight="700" fill="#FFFFFF">Kernel Boundaries &amp; Procfs</text>
      <text x="18" y="48" font-size="11" font-weight="600" fill="#10B981">Kernel-Adjacent Telemetry Hooks</text>
      <text x="18" y="74" font-size="11" fill="#94A3B8">• /proc/loadavg &amp; /proc/meminfo telemetry reads</text>
      <text x="18" y="94" font-size="11" fill="#94A3B8">• /proc/net/route default gateway host discovery</text>
      <text x="18" y="114" font-size="11" fill="#94A3B8">• cgroups v2 resource quotas &amp; process isolation</text>
      <text x="18" y="134" font-size="11" fill="#94A3B8">• eBPF-based monitoring hooks (where supported)</text>
      <text x="18" y="154" font-size="11" fill="#94A3B8">• Strict privilege separation: app stays in userspace</text>
    </g>

    <!-- Virtualization -->
    <g transform="translate(972, 55)">
      <rect width="440" height="175" rx="12" fill="#0D1322" stroke="#253556" stroke-width="1.2"/>
      <text x="18" y="28" font-size="15" font-weight="700" fill="#FFFFFF">Hardware Virtualization &amp; Isolated VMs</text>
      <text x="18" y="48" font-size="11" font-weight="600" fill="#F59E0B">QEMU / KVM / VirtualBox</text>
      <text x="18" y="74" font-size="11" fill="#94A3B8">• /dev/kvm hardware virtualization acceleration</text>
      <text x="18" y="94" font-size="11" fill="#94A3B8">• QEMU system emulator with headless VNC/SPICE</text>
      <text x="18" y="114" font-size="11" fill="#94A3B8">• VirtualBox headless automation (VBoxManage)</text>
      <text x="18" y="134" font-size="11" fill="#94A3B8">• Cloud-init automated cloud-config provisioning</text>
      <text x="18" y="154" font-size="11" fill="#94A3B8">• Isolated sandboxes for high-risk software tests</text>
    </g>
  </g>

  <!-- Footer -->
  <text x="800" y="2110" font-size="12" font-weight="600" fill="#64748B" text-anchor="middle">MarrowAI System Architecture Design (HLD) • Generated for Project Documentation • Strictly Confidential &amp; Verified</text>
</svg>"""


def build_lld_svg() -> str:
    return """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1600 2350" width="1600" height="2350" style="background:#090C15; font-family:'Plus Jakarta Sans',-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,sans-serif;">
  <defs>
    <!-- Gradients -->
    <linearGradient id="lldBg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#090C15"/>
      <stop offset="50%" stop-color="#0E1424"/>
      <stop offset="100%" stop-color="#080A10"/>
    </linearGradient>
    <linearGradient id="headerGradLLD" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#38BDF8"/>
      <stop offset="50%" stop-color="#6366F1"/>
      <stop offset="100%" stop-color="#10B981"/>
    </linearGradient>
    <linearGradient id="cardGradLLD" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#141C30" stop-opacity="0.95"/>
      <stop offset="100%" stop-color="#0E1424" stop-opacity="0.95"/>
    </linearGradient>

    <!-- Filters -->
    <filter id="shadowLLD" x="-10%" y="-10%" width="120%" height="125%">
      <feDropShadow dx="0" dy="8" stdDeviation="12" flood-color="#000" flood-opacity="0.5"/>
    </filter>

    <!-- Markers -->
    <marker id="arrowIndigo" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1 L 10 5 L 0 9 z" fill="#818CF8"/>
    </marker>
    <marker id="arrowGreenLLD" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1 L 10 5 L 0 9 z" fill="#10B981"/>
    </marker>
    <marker id="arrowCyanLLD" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1 L 10 5 L 0 9 z" fill="#38BDF8"/>
    </marker>
  </defs>

  <rect width="1600" height="2350" fill="url(#lldBg)"/>

  <!-- ==================== HEADER BLOCK ==================== -->
  <g transform="translate(80, 50)">
    <rect width="1440" height="110" rx="16" fill="#111728" stroke="#222F4C" stroke-width="1.5" filter="url(#shadowLLD)"/>
    <rect x="2" y="2" width="6" height="106" rx="3" fill="url(#headerGradLLD)"/>
    
    <text x="36" y="44" font-size="26" font-weight="800" fill="#FFFFFF" letter-spacing="-0.5">MarrowAI — Low-Level Design (LLD)</text>
    <text x="36" y="74" font-size="14" font-weight="500" fill="#94A3B8">Class Architectures, Typed Data Contracts, Method Signatures &amp; Execution Sequence Diagrams</text>
    
    <g transform="translate(1120, 28)">
      <rect width="130" height="28" rx="14" fill="#1E293B" stroke="#334155" stroke-width="1"/>
      <circle cx="14" cy="14" r="4" fill="#38BDF8"/>
      <text x="26" y="19" font-size="11" font-weight="700" fill="#E2E8F0">UML &amp; SCHEMAS</text>

      <rect x="142" y="0" width="130" height="28" rx="14" fill="#1E293B" stroke="#334155" stroke-width="1"/>
      <circle cx="156" cy="14" r="4" fill="#10B981"/>
      <text x="168" y="19" font-size="11" font-weight="700" fill="#E2E8F0">CONTRACTS v2</text>
    </g>
  </g>

  <!-- ==================== SECTION 1: TYPED DATA CONTRACTS & SCHEMAS ==================== -->
  <g transform="translate(80, 190)">
    <rect width="1440" height="340" rx="16" fill="url(#cardGradLLD)" stroke="#1F2A44" stroke-width="1.5" filter="url(#shadowLLD)"/>
    <path d="M 0 16 Q 0 0 16 0 L 1424 0 Q 1440 0 1440 16 L 1440 40 L 0 40 Z" fill="#172138"/>
    <text x="24" y="26" font-size="13" font-weight="800" fill="#38BDF8" letter-spacing="1">1. TYPED DATA CONTRACTS &amp; INTERFACE SCHEMAS (interfaces.py)</text>

    <!-- UserInput Contract -->
    <g transform="translate(24, 55)">
      <rect width="265" height="265" rx="10" fill="#0A0E1A" stroke="#233252"/>
      <rect x="0" y="0" width="265" height="32" rx="10" fill="#131D33"/>
      <text x="12" y="22" font-size="13" font-weight="700" fill="#A5B4FC">«dataclass» UserInput</text>
      <text x="12" y="55" font-size="11" font-family="'JetBrains Mono',monospace" fill="#E2E8F0">+ text: str | None</text>
      <text x="12" y="75" font-size="11" font-family="'JetBrains Mono',monospace" fill="#E2E8F0">+ audio: bytes | None</text>
      <text x="12" y="95" font-size="11" font-family="'JetBrains Mono',monospace" fill="#E2E8F0">+ source: str = "text"</text>
      <text x="12" y="115" font-size="11" font-family="'JetBrains Mono',monospace" fill="#E2E8F0">+ metadata: dict[str, Any]</text>
      <line x1="8" y1="130" x2="257" y2="130" stroke="#1E2A44"/>
      <text x="12" y="150" font-size="10.5" font-weight="600" fill="#94A3B8">Usage:</text>
      <text x="12" y="170" font-size="10.5" fill="#94A3B8">• Normalized multimodal ingest</text>
      <text x="12" y="190" font-size="10.5" fill="#94A3B8">• Voice transcript pass-through</text>
      <text x="12" y="210" font-size="10.5" fill="#94A3B8">• Client environment tagging</text>
    </g>

    <!-- TaskPlan Contract -->
    <g transform="translate(309, 55)">
      <rect width="265" height="265" rx="10" fill="#0A0E1A" stroke="#233252"/>
      <rect x="0" y="0" width="265" height="32" rx="10" fill="#131D33"/>
      <text x="12" y="22" font-size="13" font-weight="700" fill="#A5B4FC">«dataclass» TaskPlan</text>
      <text x="12" y="55" font-size="11" font-family="'JetBrains Mono',monospace" fill="#E2E8F0">+ id: str</text>
      <text x="12" y="75" font-size="11" font-family="'JetBrains Mono',monospace" fill="#E2E8F0">+ intent: str</text>
      <text x="12" y="95" font-size="11" font-family="'JetBrains Mono',monospace" fill="#E2E8F0">+ steps: list[PlanStep]</text>
      <text x="12" y="115" font-size="11" font-family="'JetBrains Mono',monospace" fill="#E2E8F0">+ constraints: list[str]</text>
      <text x="12" y="135" font-size="11" font-family="'JetBrains Mono',monospace" fill="#E2E8F0">+ risk_level: str = "low"</text>
      <line x1="8" y1="150" x2="257" y2="150" stroke="#1E2A44"/>
      <text x="12" y="170" font-size="10.5" font-weight="600" fill="#94A3B8">Guarantees:</text>
      <text x="12" y="190" font-size="10.5" fill="#94A3B8">• Strictly typed steps</text>
      <text x="12" y="210" font-size="10.5" fill="#94A3B8">• Deterministic sequence</text>
      <text x="12" y="230" font-size="10.5" fill="#94A3B8">• Never raw shell strings</text>
    </g>

    <!-- PlanStep Contract -->
    <g transform="translate(594, 55)">
      <rect width="265" height="265" rx="10" fill="#0A0E1A" stroke="#233252"/>
      <rect x="0" y="0" width="265" height="32" rx="10" fill="#131D33"/>
      <text x="12" y="22" font-size="13" font-weight="700" fill="#A5B4FC">«dataclass» PlanStep</text>
      <text x="12" y="55" font-size="11" font-family="'JetBrains Mono',monospace" fill="#E2E8F0">+ id: str</text>
      <text x="12" y="75" font-size="11" font-family="'JetBrains Mono',monospace" fill="#E2E8F0">+ action_type: str</text>
      <text x="12" y="95" font-size="11" font-family="'JetBrains Mono',monospace" fill="#E2E8F0">+ description: str</text>
      <text x="12" y="115" font-size="11" font-family="'JetBrains Mono',monospace" fill="#E2E8F0">+ tool_name: str | None</text>
      <text x="12" y="135" font-size="11" font-family="'JetBrains Mono',monospace" fill="#E2E8F0">+ parameters: dict[str, Any]</text>
      <text x="12" y="155" font-size="11" font-family="'JetBrains Mono',monospace" fill="#E2E8F0">+ approval_required: bool</text>
      <line x1="8" y1="170" x2="257" y2="170" stroke="#1E2A44"/>
      <text x="12" y="190" font-size="10.5" fill="#94A3B8">action_type in {api, cli,</text>
      <text x="12" y="208" font-size="10.5" fill="#94A3B8">file, gui, question}</text>
    </g>

    <!-- SafetyDecision Contract -->
    <g transform="translate(879, 55)">
      <rect width="265" height="265" rx="10" fill="#0A0E1A" stroke="#233252"/>
      <rect x="0" y="0" width="265" height="32" rx="10" fill="#131D33"/>
      <text x="12" y="22" font-size="13" font-weight="700" fill="#F59E0B">«dataclass» SafetyDecision</text>
      <text x="12" y="55" font-size="11" font-family="'JetBrains Mono',monospace" fill="#E2E8F0">+ decision: str</text>
      <text x="12" y="75" font-size="11" font-family="'JetBrains Mono',monospace" fill="#E2E8F0">+ reason: str</text>
      <text x="12" y="95" font-size="11" font-family="'JetBrains Mono',monospace" fill="#E2E8F0">+ confidence: float = 1.0</text>
      <text x="12" y="115" font-size="11" font-family="'JetBrains Mono',monospace" fill="#E2E8F0">+ requires_confirm: bool</text>
      <line x1="8" y1="130" x2="257" y2="130" stroke="#1E2A44"/>
      <text x="12" y="150" font-size="10.5" font-weight="600" fill="#94A3B8">Decisions:</text>
      <text x="12" y="170" font-size="10.5" fill="#10B981">• ALLOW: Execute immediately</text>
      <text x="12" y="190" font-size="10.5" fill="#F59E0B">• REVIEW: Prompt user confirm</text>
      <text x="12" y="210" font-size="10.5" fill="#EF4444">• DENY: Hard safety block</text>
    </g>

    <!-- ExecutionResult Contract -->
    <g transform="translate(1164, 55)">
      <rect width="252" height="265" rx="10" fill="#0A0E1A" stroke="#233252"/>
      <rect x="0" y="0" width="252" height="32" rx="10" fill="#131D33"/>
      <text x="12" y="22" font-size="13" font-weight="700" fill="#10B981">«dataclass» ExecutionResult</text>
      <text x="12" y="55" font-size="11" font-family="'JetBrains Mono',monospace" fill="#E2E8F0">+ status: str</text>
      <text x="12" y="75" font-size="11" font-family="'JetBrains Mono',monospace" fill="#E2E8F0">+ output: str</text>
      <text x="12" y="95" font-size="11" font-family="'JetBrains Mono',monospace" fill="#E2E8F0">+ exit_code: int | None</text>
      <text x="12" y="115" font-size="11" font-family="'JetBrains Mono',monospace" fill="#E2E8F0">+ logs: list[str]</text>
      <text x="12" y="135" font-size="11" font-family="'JetBrains Mono',monospace" fill="#E2E8F0">+ warnings: list[str]</text>
      <line x1="8" y1="150" x2="244" y2="150" stroke="#1E2A44"/>
      <text x="12" y="170" font-size="10.5" font-weight="600" fill="#94A3B8">Statuses:</text>
      <text x="12" y="190" font-size="10.5" fill="#94A3B8">• success | failed</text>
      <text x="12" y="210" font-size="10.5" fill="#94A3B8">• blocked | partial</text>
    </g>
  </g>

  <!-- ==================== SECTION 2: CORE CLASS HIERARCHY & DETAILED METHODS ==================== -->
  <g transform="translate(80, 555)">
    <rect width="1440" height="490" rx="16" fill="url(#cardGradLLD)" stroke="#1F2A44" stroke-width="1.5" filter="url(#shadowLLD)"/>
    <path d="M 0 16 Q 0 0 16 0 L 1424 0 Q 1440 0 1440 16 L 1440 40 L 0 40 Z" fill="#172138"/>
    <text x="24" y="26" font-size="13" font-weight="800" fill="#6366F1" letter-spacing="1">2. DETAILED CLASS ARCHITECTURE &amp; METHOD SIGNATURES</text>

    <!-- MarrowAssistant -->
    <g transform="translate(24, 55)">
      <rect width="330" height="415" rx="10" fill="#0A0E1A" stroke="#253556"/>
      <rect x="0" y="0" width="330" height="34" rx="10" fill="#162038"/>
      <text x="14" y="23" font-size="14" font-weight="700" fill="#FFFFFF">MarrowAssistant</text>
      <text x="14" y="55" font-size="10.5" font-family="'JetBrains Mono',monospace" fill="#94A3B8">- model_provider: ModelProvider</text>
      <text x="14" y="73" font-size="10.5" font-family="'JetBrains Mono',monospace" fill="#94A3B8">- planner: Planner</text>
      <text x="14" y="91" font-size="10.5" font-family="'JetBrains Mono',monospace" fill="#94A3B8">- safety: RiskClassifier</text>
      <text x="14" y="109" font-size="10.5" font-family="'JetBrains Mono',monospace" fill="#94A3B8">- tool_router: ToolRouter</text>
      <text x="14" y="127" font-size="10.5" font-family="'JetBrains Mono',monospace" fill="#94A3B8">- executor: Executor</text>
      <text x="14" y="145" font-size="10.5" font-family="'JetBrains Mono',monospace" fill="#94A3B8">- audit: AuditLogger</text>
      <text x="14" y="163" font-size="10.5" font-family="'JetBrains Mono',monospace" fill="#94A3B8">- governor: ResourceGovernor</text>
      <text x="14" y="181" font-size="10.5" font-family="'JetBrains Mono',monospace" fill="#94A3B8">- voice_engine: OfflineVoiceEngine</text>
      <line x1="8" y1="195" x2="322" y2="195" stroke="#1E2A44"/>
      <text x="14" y="215" font-size="10.5" font-family="'JetBrains Mono',monospace" fill="#A5B4FC">+ process(prompt, confirmed=False,</text>
      <text x="32" y="233" font-size="10.5" font-family="'JetBrains Mono',monospace" fill="#A5B4FC">password=None) -> dict</text>
      <text x="14" y="255" font-size="10.5" font-family="'JetBrains Mono',monospace" fill="#A5B4FC">+ execute_plan(plan: TaskPlan) -> dict</text>
      <text x="14" y="275" font-size="10.5" font-family="'JetBrains Mono',monospace" fill="#A5B4FC">+ check_telemetry() -> TelemetryData</text>
      <text x="14" y="295" font-size="10.5" font-family="'JetBrains Mono',monospace" fill="#A5B4FC">+ is_conversational(intent) -> bool</text>
      <line x1="8" y1="310" x2="322" y2="310" stroke="#1E2A44"/>
      <text x="14" y="330" font-size="10.5" fill="#94A3B8">Top-level orchestration facade.</text>
      <text x="14" y="348" font-size="10.5" fill="#94A3B8">Coordinates cognitive flow, security</text>
      <text x="14" y="366" font-size="10.5" fill="#94A3B8">gates, tool execution, and voice alerts.</text>
    </g>

    <!-- Planner & Safety -->
    <g transform="translate(378, 55)">
      <rect width="330" height="415" rx="10" fill="#0A0E1A" stroke="#253556"/>
      <rect x="0" y="0" width="330" height="34" rx="10" fill="#162038"/>
      <text x="14" y="23" font-size="14" font-weight="700" fill="#FFFFFF">Planner &amp; RiskClassifier</text>
      
      <!-- Planner section -->
      <text x="14" y="55" font-size="11" font-weight="700" fill="#38BDF8">Planner (planner.py)</text>
      <text x="14" y="75" font-size="10.5" font-family="'JetBrains Mono',monospace" fill="#E2E8F0">+ plan(prompt: str) -> TaskPlan</text>
      <text x="14" y="93" font-size="10.5" font-family="'JetBrains Mono',monospace" fill="#E2E8F0">+ _map_intent(prompt: str) -> str</text>
      <text x="14" y="111" font-size="10.5" font-family="'JetBrains Mono',monospace" fill="#E2E8F0">+ _extract_parameters(prompt) -> dict</text>
      <text x="14" y="129" font-size="10.5" font-family="'JetBrains Mono',monospace" fill="#E2E8F0">+ _map_vm_creation(prompt) -> TaskPlan</text>
      <text x="14" y="147" font-size="10.5" font-family="'JetBrains Mono',monospace" fill="#E2E8F0">+ _map_model_management(p) -> TaskPlan</text>

      <line x1="8" y1="165" x2="322" y2="165" stroke="#1E2A44"/>

      <!-- Safety section -->
      <text x="14" y="185" font-size="11" font-weight="700" fill="#F59E0B">RiskClassifier (safety.py)</text>
      <text x="14" y="205" font-size="10.5" font-family="'JetBrains Mono',monospace" fill="#E2E8F0">+ evaluate(step: PlanStep) -> SafetyDecision</text>
      <text x="14" y="223" font-size="10.5" font-family="'JetBrains Mono',monospace" fill="#E2E8F0">+ classify_risk(action_type) -> str</text>
      <text x="14" y="241" font-size="10.5" font-family="'JetBrains Mono',monospace" fill="#E2E8F0">+ is_destructive(cmd_str: str) -> bool</text>
      <text x="14" y="259" font-size="10.5" font-family="'JetBrains Mono',monospace" fill="#E2E8F0">+ requires_sudo(step: PlanStep) -> bool</text>

      <line x1="8" y1="275" x2="322" y2="275" stroke="#1E2A44"/>
      <text x="14" y="295" font-size="10.5" fill="#94A3B8">Strict separation of concerns:</text>
      <text x="14" y="313" font-size="10.5" fill="#94A3B8">Planner proposes; Classifier decides.</text>
      <text x="14" y="331" font-size="10.5" fill="#94A3B8">Policy gate blocks unvetted actions.</text>
    </g>

    <!-- OfflineModelManager & ResourceGovernor -->
    <g transform="translate(732, 55)">
      <rect width="340" height="415" rx="10" fill="#0A0E1A" stroke="#253556"/>
      <rect x="0" y="0" width="340" height="34" rx="10" fill="#162038"/>
      <text x="14" y="23" font-size="14" font-weight="700" fill="#FFFFFF">ModelManager &amp; Governor</text>

      <!-- Model Manager -->
      <text x="14" y="55" font-size="11" font-weight="700" fill="#10B981">OfflineModelManager (model_manager.py)</text>
      <text x="14" y="75" font-size="10.5" font-family="'JetBrains Mono',monospace" fill="#E2E8F0">+ discover_ollama_base_url() -> str</text>
      <text x="14" y="93" font-size="10.5" font-family="'JetBrains Mono',monospace" fill="#E2E8F0">+ is_available() -> bool</text>
      <text x="14" y="111" font-size="10.5" font-family="'JetBrains Mono',monospace" fill="#E2E8F0">+ download_model(name, cb, voice) -> tuple</text>
      <text x="14" y="129" font-size="10.5" font-family="'JetBrains Mono',monospace" fill="#E2E8F0">+ list_local_models_detailed() -> list[dict]</text>
      <text x="14" y="147" font-size="10.5" font-family="'JetBrains Mono',monospace" fill="#E2E8F0">+ delete_model(name: str) -> tuple[bool, str]</text>
      <text x="14" y="165" font-size="10.5" font-family="'JetBrains Mono',monospace" fill="#E2E8F0">+ start_service() -> tuple[bool, str]</text>

      <line x1="8" y1="180" x2="332" y2="180" stroke="#1E2A44"/>

      <!-- Resource Governor -->
      <text x="14" y="200" font-size="11" font-weight="700" fill="#38BDF8">ResourceGovernor (governor.py)</text>
      <text x="14" y="220" font-size="10.5" font-family="'JetBrains Mono',monospace" fill="#E2E8F0">+ get_telemetry() -> TelemetryData</text>
      <text x="14" y="238" font-size="10.5" font-family="'JetBrains Mono',monospace" fill="#E2E8F0">+ is_safe_to_execute() -> tuple[bool, dict]</text>
      <text x="14" y="256" font-size="10.5" font-family="'JetBrains Mono',monospace" fill="#E2E8F0">+ enforce_limits() -> None</text>
      <text x="14" y="274" font-size="10.5" font-family="'JetBrains Mono',monospace" fill="#E2E8F0">+ detect_hypervisors() -> dict</text>

      <line x1="8" y1="290" x2="332" y2="290" stroke="#1E2A44"/>
      <text x="14" y="310" font-size="10.5" fill="#94A3B8">Models stored in ~/.ollama/models</text>
      <text x="14" y="328" font-size="10.5" fill="#94A3B8">Proactive throttling protects CPU/RAM</text>
    </g>

    <!-- VoiceEngine & VectorDB -->
    <g transform="translate(1096, 55)">
      <rect width="320" height="415" rx="10" fill="#0A0E1A" stroke="#253556"/>
      <rect x="0" y="0" width="320" height="34" rx="10" fill="#162038"/>
      <text x="14" y="23" font-size="14" font-weight="700" fill="#FFFFFF">VoiceEngine &amp; VectorDB</text>

      <!-- Voice Engine -->
      <text x="14" y="55" font-size="11" font-weight="700" fill="#F59E0B">OfflineVoiceEngine (voice_engine.py)</text>
      <text x="14" y="75" font-size="10.5" font-family="'JetBrains Mono',monospace" fill="#E2E8F0">+ synthesize_neural_audio() -> bytes</text>
      <text x="14" y="93" font-size="10.5" font-family="'JetBrains Mono',monospace" fill="#E2E8F0">+ synthesize_offline_wav() -> bytes</text>
      <text x="14" y="111" font-size="10.5" font-family="'JetBrains Mono',monospace" fill="#E2E8F0">+ speak(text: str) -> VoiceStatus</text>
      <text x="14" y="129" font-size="10.5" font-family="'JetBrains Mono',monospace" fill="#E2E8F0">+ set_profile(name: str) -> None</text>
      <text x="14" y="147" font-size="10.5" font-family="'JetBrains Mono',monospace" fill="#E2E8F0">+ status() -> dict[str, Any]</text>

      <line x1="8" y1="165" x2="312" y2="165" stroke="#1E2A44"/>

      <!-- Vector DB -->
      <text x="14" y="185" font-size="11" font-weight="700" fill="#A5B4FC">VectorDatabase (vector_db.py)</text>
      <text x="14" y="205" font-size="10.5" font-family="'JetBrains Mono',monospace" fill="#E2E8F0">+ SemanticEmbedder.encode(text) -> list</text>
      <text x="14" y="223" font-size="10.5" font-family="'JetBrains Mono',monospace" fill="#E2E8F0">+ add_document(text, meta) -> str</text>
      <text x="14" y="241" font-size="10.5" font-family="'JetBrains Mono',monospace" fill="#E2E8F0">+ similarity_search(query, k) -> list</text>
      <text x="14" y="259" font-size="10.5" font-family="'JetBrains Mono',monospace" fill="#E2E8F0">+ cosine_similarity(v1, v2) -> float</text>

      <line x1="8" y1="275" x2="312" y2="275" stroke="#1E2A44"/>
      <text x="14" y="295" font-size="10.5" fill="#94A3B8">Studio-grade Edge-TTS neural speech.</text>
      <text x="14" y="313" font-size="10.5" fill="#94A3B8">Zero-dependency 256-d offline embeddings</text>
      <text x="14" y="331" font-size="10.5" fill="#94A3B8">with SQLite binary vector storage.</text>
    </g>
  </g>

  <!-- ==================== SECTION 3: SEQUENCE & INTERACTION FLOWS ==================== -->
  <g transform="translate(80, 1070)">
    <rect width="1440" height="1220" rx="16" fill="url(#cardGradLLD)" stroke="#1F2A44" stroke-width="1.5" filter="url(#shadowLLD)"/>
    <path d="M 0 16 Q 0 0 16 0 L 1424 0 Q 1440 0 1440 16 L 1440 40 L 0 40 Z" fill="#172138"/>
    <text x="24" y="26" font-size="13" font-weight="800" fill="#10B981" letter-spacing="1">3. DETAILED EXECUTION &amp; INTERACTION SEQUENCE DIAGRAMS</text>

    <!-- Sequence 1: Prompt-to-Execution Flow with Safety Gate -->
    <g transform="translate(24, 60)">
      <text x="0" y="0" font-size="14" font-weight="700" fill="#FFFFFF">Sequence 3.1: Task Execution with Zero-Trust Safety Approval Gate</text>
      
      <!-- Lifeline Headers -->
      <g transform="translate(0, 20)">
        <rect x="0" y="0" width="120" height="30" rx="6" fill="#1E293B" stroke="#334155"/>
        <text x="60" y="19" font-size="11" font-weight="700" fill="#FFFFFF" text-anchor="middle">User / UI</text>
        <line x1="60" y1="30" x2="60" y2="460" stroke="#334155" stroke-dasharray="4 4"/>

        <rect x="230" y="0" width="130" height="30" rx="6" fill="#1E293B" stroke="#334155"/>
        <text x="295" y="19" font-size="11" font-weight="700" fill="#FFFFFF" text-anchor="middle">MarrowAssistant</text>
        <line x1="295" y1="30" x2="295" y2="460" stroke="#334155" stroke-dasharray="4 4"/>

        <rect x="470" y="0" width="110" height="30" rx="6" fill="#1E293B" stroke="#334155"/>
        <text x="525" y="19" font-size="11" font-weight="700" fill="#FFFFFF" text-anchor="middle">Planner</text>
        <line x1="525" y1="30" x2="525" y2="460" stroke="#334155" stroke-dasharray="4 4"/>

        <rect x="690" y="0" width="130" height="30" rx="6" fill="#1E293B" stroke="#334155"/>
        <text x="755" y="19" font-size="11" font-weight="700" fill="#FFFFFF" text-anchor="middle">RiskClassifier</text>
        <line x1="755" y1="30" x2="755" y2="460" stroke="#334155" stroke-dasharray="4 4"/>

        <rect x="930" y="0" width="120" height="30" rx="6" fill="#1E293B" stroke="#334155"/>
        <text x="990" y="19" font-size="11" font-weight="700" fill="#FFFFFF" text-anchor="middle">ToolRouter</text>
        <line x1="990" y1="30" x2="990" y2="460" stroke="#334155" stroke-dasharray="4 4"/>

        <rect x="1160" y="0" width="110" height="30" rx="6" fill="#1E293B" stroke="#334155"/>
        <text x="1215" y="19" font-size="11" font-weight="700" fill="#FFFFFF" text-anchor="middle">Executor</text>
        <line x1="1215" y1="30" x2="1215" y2="460" stroke="#334155" stroke-dasharray="4 4"/>

        <rect x="1300" y="0" width="90" height="30" rx="6" fill="#1E293B" stroke="#334155"/>
        <text x="1345" y="19" font-size="11" font-weight="700" fill="#FFFFFF" text-anchor="middle">AuditLog</text>
        <line x1="1345" y1="30" x2="1345" y2="460" stroke="#334155" stroke-dasharray="4 4"/>
      </g>

      <!-- Message Arrows -->
      <g transform="translate(0, 70)">
        <!-- 1: Send prompt -->
        <line x1="60" y1="20" x2="295" y2="20" stroke="#6366F1" stroke-width="1.8" marker-end="url(#arrowIndigo)"/>
        <text x="175" y="14" font-size="10.5" fill="#E2E8F0" text-anchor="middle">1. process(prompt, confirmed=False)</text>

        <!-- 2: Plan -->
        <line x1="295" y1="50" x2="525" y2="50" stroke="#6366F1" stroke-width="1.8" marker-end="url(#arrowIndigo)"/>
        <text x="410" y="44" font-size="10.5" fill="#E2E8F0" text-anchor="middle">2. plan(prompt)</text>

        <!-- 3: Return plan -->
        <line x1="525" y1="80" x2="295" y2="80" stroke="#38BDF8" stroke-dasharray="3 3" stroke-width="1.5" marker-end="url(#arrowCyanLLD)"/>
        <text x="410" y="74" font-size="10.5" fill="#BAE6FD" text-anchor="middle">3. TaskPlan (steps, risk_level)</text>

        <!-- 4: Evaluate safety -->
        <line x1="295" y1="110" x2="755" y2="110" stroke="#F59E0B" stroke-width="1.8" marker-end="url(#arrowIndigo)"/>
        <text x="525" y="104" font-size="10.5" fill="#FDE68A" text-anchor="middle">4. evaluate(step)</text>

        <!-- 5: Decision -->
        <line x1="755" y1="140" x2="295" y2="140" stroke="#F59E0B" stroke-dasharray="3 3" stroke-width="1.5" marker-end="url(#arrowIndigo)"/>
        <text x="525" y="134" font-size="10.5" fill="#FDE68A" text-anchor="middle">5. SafetyDecision(requires_confirmation=True)</text>

        <!-- Alt: Confirmation required -->
        <rect x="50" y="165" width="720" height="75" rx="6" fill="#241908" stroke="#F59E0B" stroke-dasharray="3 3"/>
        <text x="60" y="182" font-size="10" font-weight="700" fill="#F59E0B">[ALT: HIGH-RISK CONFIRMATION PATH]</text>
        <line x1="295" y1="195" x2="60" y2="195" stroke="#F59E0B" stroke-width="1.8" marker-end="url(#arrowIndigo)"/>
        <text x="175" y="190" font-size="10.5" fill="#FDE68A" text-anchor="middle">requires_confirmation card displayed</text>
        <line x1="60" y1="225" x2="295" y2="225" stroke="#10B981" stroke-width="1.8" marker-end="url(#arrowGreenLLD)"/>
        <text x="175" y="220" font-size="10.5" fill="#A7F3D0" text-anchor="middle">confirmAction(proceed=True, password=pwd)</text>

        <!-- 6: Route tool -->
        <line x1="295" y1="260" x2="990" y2="260" stroke="#10B981" stroke-width="1.8" marker-end="url(#arrowGreenLLD)"/>
        <text x="640" y="254" font-size="10.5" fill="#A7F3D0" text-anchor="middle">6. route(step, password=pwd) -> ToolCall</text>

        <!-- 7: Execute -->
        <line x1="990" y1="290" x2="1215" y2="290" stroke="#10B981" stroke-width="1.8" marker-end="url(#arrowGreenLLD)"/>
        <text x="1100" y="284" font-size="10.5" fill="#A7F3D0" text-anchor="middle">7. execute(tool_call)</text>

        <!-- 8: Return result -->
        <line x1="1215" y1="320" x2="295" y2="320" stroke="#38BDF8" stroke-dasharray="3 3" stroke-width="1.5" marker-end="url(#arrowCyanLLD)"/>
        <text x="755" y="314" font-size="10.5" fill="#BAE6FD" text-anchor="middle">8. ExecutionResult(status="success", output="...")</text>

        <!-- 9: Write audit -->
        <line x1="295" y1="350" x2="1345" y2="350" stroke="#6366F1" stroke-width="1.8" marker-end="url(#arrowIndigo)"/>
        <text x="820" y="344" font-size="10.5" fill="#C7D2FE" text-anchor="middle">9. log_action(prompt, plan, decision, result)</text>

        <!-- 10: Feedback -->
        <line x1="295" y1="380" x2="60" y2="380" stroke="#10B981" stroke-width="1.8" marker-end="url(#arrowGreenLLD)"/>
        <text x="175" y="374" font-size="10.5" fill="#A7F3D0" text-anchor="middle">10. UI Update + Voice Output</text>
      </g>
    </g>

    <!-- Sequence 2: Real-time Model Pulling & SSE Streaming -->
    <g transform="translate(24, 570)">
      <text x="0" y="0" font-size="14" font-weight="700" fill="#FFFFFF">Sequence 3.2: Real-Time Model Pulling &amp; Server-Sent Event (SSE) Streaming</text>
      
      <g transform="translate(0, 20)">
        <rect x="0" y="0" width="140" height="30" rx="6" fill="#1E293B" stroke="#334155"/>
        <text x="70" y="19" font-size="11" font-weight="700" fill="#FFFFFF" text-anchor="middle">Web Client (SSE)</text>
        <line x1="70" y1="30" x2="70" y2="280" stroke="#334155" stroke-dasharray="4 4"/>

        <rect x="350" y="0" width="160" height="30" rx="6" fill="#1E293B" stroke="#334155"/>
        <text x="430" y="19" font-size="11" font-weight="700" fill="#FFFFFF" text-anchor="middle">MarrowWebHandler</text>
        <line x1="430" y1="30" x2="430" y2="280" stroke="#334155" stroke-dasharray="4 4"/>

        <rect x="750" y="0" width="170" height="30" rx="6" fill="#1E293B" stroke="#334155"/>
        <text x="835" y="19" font-size="11" font-weight="700" fill="#FFFFFF" text-anchor="middle">OfflineModelManager</text>
        <line x1="835" y1="30" x2="835" y2="280" stroke="#334155" stroke-dasharray="4 4"/>

        <rect x="1170" y="0" width="150" height="30" rx="6" fill="#1E293B" stroke="#334155"/>
        <text x="1245" y="19" font-size="11" font-weight="700" fill="#FFFFFF" text-anchor="middle">Ollama REST API</text>
        <line x1="1245" y1="30" x2="1245" y2="280" stroke="#334155" stroke-dasharray="4 4"/>
      </g>

      <g transform="translate(0, 70)">
        <!-- 1: EventSource connect -->
        <line x1="70" y1="20" x2="430" y2="20" stroke="#38BDF8" stroke-width="1.8" marker-end="url(#arrowCyanLLD)"/>
        <text x="250" y="14" font-size="10.5" fill="#BAE6FD" text-anchor="middle">1. GET /api/pull_stream?model=llama3.2</text>

        <!-- 2: Download model -->
        <line x1="430" y1="50" x2="835" y2="50" stroke="#6366F1" stroke-width="1.8" marker-end="url(#arrowIndigo)"/>
        <text x="632" y="44" font-size="10.5" fill="#C7D2FE" text-anchor="middle">2. download_model(model_name, progress_cb)</text>

        <!-- 3: POST to Ollama -->
        <line x1="835" y1="80" x2="1245" y2="80" stroke="#10B981" stroke-width="1.8" marker-end="url(#arrowGreenLLD)"/>
        <text x="1040" y="74" font-size="10.5" fill="#A7F3D0" text-anchor="middle">3. POST /api/pull {"name":"llama3.2","stream":true}</text>

        <!-- 4: Stream chunks -->
        <line x1="1245" y1="110" x2="835" y2="110" stroke="#10B981" stroke-dasharray="3 3" stroke-width="1.5" marker-end="url(#arrowGreenLLD)"/>
        <text x="1040" y="104" font-size="10.5" fill="#A7F3D0" text-anchor="middle">4. stream events (completed, total)</text>

        <!-- 5: Progress callback to SSE -->
        <line x1="835" y1="140" x2="430" y2="140" stroke="#38BDF8" stroke-width="1.8" marker-end="url(#arrowCyanLLD)"/>
        <text x="632" y="134" font-size="10.5" fill="#BAE6FD" text-anchor="middle">5. on_progress(pct, detail, comp, tot)</text>

        <!-- 6: SSE event to client -->
        <line x1="430" y1="170" x2="70" y2="170" stroke="#38BDF8" stroke-dasharray="3 3" stroke-width="1.5" marker-end="url(#arrowCyanLLD)"/>
        <text x="250" y="164" font-size="10.5" fill="#BAE6FD" text-anchor="middle">6. data: {"percent": 50.0, "detail": "...", "spoken": "..."}</text>

        <!-- 7: Milestones & completion -->
        <line x1="835" y1="200" x2="430" y2="200" stroke="#10B981" stroke-width="1.8" marker-end="url(#arrowGreenLLD)"/>
        <text x="632" y="194" font-size="10.5" fill="#A7F3D0" text-anchor="middle">7. download finished (verified locally)</text>

        <line x1="430" y1="230" x2="70" y2="230" stroke="#10B981" stroke-width="1.8" marker-end="url(#arrowGreenLLD)"/>
        <text x="250" y="224" font-size="10.5" fill="#A7F3D0" text-anchor="middle">8. data: {"done": true} -> Dropdown auto-refreshed</text>
      </g>
    </g>

    <!-- Sequence 3: Natural Neural Voice Pipeline -->
    <g transform="translate(24, 910)">
      <text x="0" y="0" font-size="14" font-weight="700" fill="#FFFFFF">Sequence 3.3: Natural Studio-Quality Neural Voice Synthesis Pipeline</text>

      <g transform="translate(0, 20)">
        <rect x="0" y="0" width="130" height="30" rx="6" fill="#1E293B" stroke="#334155"/>
        <text x="65" y="19" font-size="11" font-weight="700" fill="#FFFFFF" text-anchor="middle">Client UI / Audio</text>
        <line x1="65" y1="30" x2="65" y2="230" stroke="#334155" stroke-dasharray="4 4"/>

        <rect x="360" y="0" width="150" height="30" rx="6" fill="#1E293B" stroke="#334155"/>
        <text x="435" y="19" font-size="11" font-weight="700" fill="#FFFFFF" text-anchor="middle">/api/tts (WebHandler)</text>
        <line x1="435" y1="30" x2="435" y2="230" stroke="#334155" stroke-dasharray="4 4"/>

        <rect x="760" y="0" width="160" height="30" rx="6" fill="#1E293B" stroke="#334155"/>
        <text x="840" y="19" font-size="11" font-weight="700" fill="#FFFFFF" text-anchor="middle">OfflineVoiceEngine</text>
        <line x1="840" y1="30" x2="840" y2="230" stroke="#334155" stroke-dasharray="4 4"/>

        <rect x="1170" y="0" width="150" height="30" rx="6" fill="#1E293B" stroke="#334155"/>
        <text x="1245" y="19" font-size="11" font-weight="700" fill="#FFFFFF" text-anchor="middle">Neural Edge-TTS / SAPI</text>
        <line x1="1245" y1="30" x2="1245" y2="230" stroke="#334155" stroke-dasharray="4 4"/>
      </g>

      <g transform="translate(0, 70)">
        <line x1="65" y1="20" x2="435" y2="20" stroke="#F59E0B" stroke-width="1.8" marker-end="url(#arrowIndigo)"/>
        <text x="250" y="14" font-size="10.5" fill="#FDE68A" text-anchor="middle">1. GET /api/tts?voice=indian_female&amp;text=...</text>

        <line x1="435" y1="50" x2="840" y2="50" stroke="#6366F1" stroke-width="1.8" marker-end="url(#arrowIndigo)"/>
        <text x="637" y="44" font-size="10.5" fill="#C7D2FE" text-anchor="middle">2. synthesize_neural_audio(clean_text, profile)</text>

        <line x1="840" y1="80" x2="1245" y2="80" stroke="#10B981" stroke-width="1.8" marker-end="url(#arrowGreenLLD)"/>
        <text x="1042" y="74" font-size="10.5" fill="#A7F3D0" text-anchor="middle">3. edge_tts.Communicate(clean_text, "en-IN-NeerjaNeural")</text>

        <line x1="1245" y1="110" x2="840" y2="110" stroke="#10B981" stroke-dasharray="3 3" stroke-width="1.5" marker-end="url(#arrowGreenLLD)"/>
        <text x="1042" y="104" font-size="10.5" fill="#A7F3D0" text-anchor="middle">4. stream MP3 audio bytes (>200 B)</text>

        <line x1="840" y1="140" x2="435" y2="140" stroke="#38BDF8" stroke-width="1.8" marker-end="url(#arrowCyanLLD)"/>
        <text x="637" y="134" font-size="10.5" fill="#BAE6FD" text-anchor="middle">5. Cache in _AUDIO_CACHE &amp; return audio_data</text>

        <line x1="435" y1="170" x2="65" y2="170" stroke="#10B981" stroke-width="1.8" marker-end="url(#arrowGreenLLD)"/>
        <text x="250" y="164" font-size="10.5" fill="#A7F3D0" text-anchor="middle">6. HTTP 200 (audio/mpeg) -> Audio playback + Waveform animation</text>
      </g>
    </g>
  </g>

  <!-- Footer -->
  <text x="800" y="2315" font-size="12" font-weight="600" fill="#64748B" text-anchor="middle">MarrowAI Low-Level Design (LLD) • Generated for Project Documentation • Strictly Confidential &amp; Verified</text>
</svg>"""


def render_svg_to_png_custom(svg_path: Path, png_path: Path, title: str, subtitle: str, layers_data: list):
    """
    Renders a clean high-resolution blueprint PNG image representing the system design
    using PIL ImageDraw to ensure reliable raster image generation.
    """
    width, height = 1600, 2200
    img = Image.new("RGBA", (width, height), (9, 12, 21, 255))
    draw = ImageDraw.Draw(img)

    # Gradient background simulation with rectangles
    for y in range(height):
        ratio = y / height
        r = int(9 + ratio * 5)
        g = int(12 + ratio * 8)
        b = int(21 + ratio * 15)
        draw.line([(0, y), (width, y)], fill=(r, g, b, 255))

    # Header Card
    draw.rounded_rectangle([(60, 40), (1540, 150)], radius=14, fill=(17, 23, 40, 255), outline=(34, 47, 76, 255), width=2)
    draw.rounded_rectangle([(62, 42), (70, 148)], radius=4, fill=(99, 102, 241, 255))
    draw.text((95, 60), title, fill=(255, 255, 255, 255))
    draw.text((95, 95), subtitle, fill=(148, 163, 184, 255))

    # Layers
    y_curr = 180
    for layer in layers_data:
        h = layer.get("height", 230)
        draw.rounded_rectangle([(60, y_curr), (1540, y_curr + h)], radius=14, fill=(19, 26, 44, 240), outline=(31, 42, 68, 255), width=2)
        draw.rounded_rectangle([(60, y_curr), (1540, y_curr + 36)], radius=14, fill=(23, 33, 56, 255))
        draw.text((80, y_curr + 10), layer["title"], fill=layer.get("title_color", (56, 189, 248, 255)))

        # Sub-boxes
        x_sub = 80
        box_w = (1420 - (len(layer["boxes"]) - 1) * 20) // len(layer["boxes"])
        for box in layer["boxes"]:
            draw.rounded_rectangle([(x_sub, y_curr + 50), (x_sub + box_w, y_curr + h - 20)], radius=10, fill=(13, 19, 34, 255), outline=(37, 53, 86, 255), width=1)
            draw.text((x_sub + 14, y_curr + 65), box["name"], fill=(255, 255, 255, 255))
            draw.text((x_sub + 14, y_curr + 85), box.get("sub", ""), fill=box.get("sub_color", (99, 102, 241, 255)))
            
            y_item = y_curr + 110
            for item in box.get("items", []):
                draw.text((x_sub + 14, y_item), "• " + item, fill=(148, 163, 184, 255))
                y_item += 18
            x_sub += box_w + 20

        y_curr += h + 30

    img.save(str(png_path), format="PNG")
    print(f"Generated PNG: {png_path}")


def main():
    hld_svg_path = DOCS_DIR / "HLD_SYSTEM_DESIGN.svg"
    lld_svg_path = DOCS_DIR / "LLD_SYSTEM_DESIGN.svg"
    hld_png_path = DOCS_DIR / "HLD_SYSTEM_DESIGN.png"
    lld_png_path = DOCS_DIR / "LLD_SYSTEM_DESIGN.png"

    # Write SVGs
    hld_svg_content = build_hld_svg()
    lld_svg_content = build_lld_svg()

    with open(hld_svg_path, "w", encoding="utf-8") as f:
        f.write(hld_svg_content)
    print(f"Generated HLD SVG: {hld_svg_path}")

    with open(lld_svg_path, "w", encoding="utf-8") as f:
        f.write(lld_svg_content)
    print(f"Generated LLD SVG: {lld_svg_path}")

    # Generate High-Resolution PNGs
    hld_layers = [
        {
            "title": "LAYER 1: USER CLIENT & PRESENTATION INTERFACES",
            "title_color": (56, 189, 248, 255),
            "height": 220,
            "boxes": [
                {
                    "name": "Web GUI Workstation",
                    "sub": "ThreadingHTTPServer (:8765)",
                    "sub_color": (99, 102, 241, 255),
                    "items": ["Dark Obsidian Frosted Glass UI", "Dynamic Model Selector (Ready)", "Server-Sent Events (/api/pull_stream)", "Speech Waveform & Auto-Listen"]
                },
                {
                    "name": "Tkinter Desktop GUI",
                    "sub": "MarrowAIWindow (Clam)",
                    "sub_color": (56, 189, 248, 255),
                    "items": ["Real-time Telemetry Meters", "Grouped Installed Model Combobox", "Determinate Progressbar (0-100%)", "Security Audit Log Modal Viewer"]
                },
                {
                    "name": "CLI & Shell Suite",
                    "sub": "marrowai / marrowai-chat",
                    "sub_color": (16, 185, 129, 255),
                    "items": ["Interactive REPL with Safety Gate", "Headless Script & Batch Mode", "marrowai-doctor Diagnostic Probe", "marrowai-scaffold Project Init"]
                },
                {
                    "name": "Voice Ingest & Speech",
                    "sub": "Web Speech + Neural Edge-TTS",
                    "sub_color": (245, 158, 11, 255),
                    "items": ["Web Speech Dictation (en-IN)", "Microsoft Neural TTS (Studio)", "Conversational Turn-Taking Loop", "Sub-5ms In-Memory LRU Audio Cache"]
                }
            ]
        },
        {
            "title": "LAYER 2: MULTIMODAL INGESTION & NORMALIZATION",
            "title_color": (56, 189, 248, 255),
            "height": 190,
            "boxes": [
                {
                    "name": "STT Abstraction",
                    "sub": "Speech-To-Text Pipeline",
                    "items": ["Browser SpeechRec API", "FFmpeg fallback pipeline", "Audio chunk validation"]
                },
                {
                    "name": "Input Normalizer",
                    "sub": "Sanitization & Classification",
                    "items": ["Sanitizes control tokens", "Classifies intent types", "Conversational vs Execution"]
                },
                {
                    "name": "Session Context",
                    "sub": "State & Cache Storage",
                    "items": ["Session turn history", "Active model selection", "Security confirmation state"]
                }
            ]
        },
        {
            "title": "LAYER 3: COGNITIVE & PLANNING ENGINE (LLM OUTSIDE PRIVILEGED PATH)",
            "title_color": (99, 102, 241, 255),
            "height": 230,
            "boxes": [
                {
                    "name": "MarrowAssistant Facade",
                    "sub": "Core Orchestrator",
                    "items": ["Manages request lifecycle", "Enforces deterministic planning", "Handles conversational branches", "Triggers voice & UI responses"]
                },
                {
                    "name": "Autonomous Planner",
                    "sub": "Deterministic Task Decomp",
                    "items": ["Regex & Semantic intent parsing", "VM creation pipeline planning", "Scaffolding & test generation", "Emits typed TaskPlan contract"]
                },
                {
                    "name": "Model Provider Layer",
                    "sub": "OllamaProvider / Local",
                    "items": ["Endpoint auto-discovery (WSL/host)", "Ollama REST client integration", "JSON schema enforcement", "Strictly outside execution path"]
                },
                {
                    "name": "Typed Data Contracts",
                    "sub": "interfaces.py Validation",
                    "items": ["TaskPlan (id, intent, steps)", "PlanStep (tool, params)", "NO raw shell string emission", "Immutable representation"]
                }
            ]
        },
        {
            "title": "LAYER 4: ZERO-TRUST SAFETY, SECURITY & GOVERNANCE GATEWAY",
            "title_color": (245, 158, 11, 255),
            "height": 230,
            "boxes": [
                {
                    "name": "Risk Classifier",
                    "sub": "Three-Tier Evaluation",
                    "items": ["LOW: Safe reads, telemetry", "MEDIUM: File scaffolding, edits", "HIGH: Sudo, VM creation, packages", "Evaluates tool & target args"]
                },
                {
                    "name": "Safety Policy Gate",
                    "sub": "ALLOW / REVIEW / DENY",
                    "items": ["Checks against policy rules", "Rejects prohibited commands", "Flags actions for authorization", "Emits SafetyDecision contract"]
                },
                {
                    "name": "User Authorization Gate",
                    "sub": "Interactive Confirmation",
                    "items": ["Halts execution for HIGH risk", "Displays password dialog", "Requires explicit approval", "Clean cancellation path"]
                },
                {
                    "name": "Security Audit Logger",
                    "sub": "Append-Only Audit Trail",
                    "items": ["Records timestamps & prompts", "Logs tool calls & exit codes", "Secret masking (no passwords)", "Inspectable in UI modal"]
                }
            ]
        },
        {
            "title": "LAYER 5: TOOL ROUTING & ORCHESTRATION ENGINE",
            "title_color": (16, 185, 129, 255),
            "height": 230,
            "boxes": [
                {
                    "name": "Tool Router",
                    "sub": "Schema Validation",
                    "items": ["Tool registration map", "Argument type coercion", "Timeout enforcement", "Dispatches to executors"]
                },
                {
                    "name": "VM Manager",
                    "sub": "Hypervisor Automation",
                    "items": ["KVM / QEMU / VBox detect", "Automated ISO verification", "Cloud-init unattended setup", "Arch & Ubuntu VM deploy"]
                },
                {
                    "name": "ManageModelsTool",
                    "sub": "Model Operations",
                    "items": ["Pull / delete / list models", "Preset vs custom tags", "Progress streaming hook", "Active model switching"]
                },
                {
                    "name": "Scaffold & Diagnostics",
                    "sub": "Workspace & Health",
                    "items": ["FastAPI / Go scaffolding", "SystemDiagnosticsTool", "Disk & RAM telemetry", "Test suite runner"]
                },
                {
                    "name": "Execution Engine",
                    "sub": "executor.py Subprocess",
                    "items": ["Bounded subprocess exec", "Exit code capture", "Sandboxed working dir", "GUI automation fallback"]
                }
            ]
        },
        {
            "title": "LAYER 6: OFFLINE SUBSYSTEMS, RESOURCE GOVERNOR & PERSISTENCE",
            "title_color": (56, 189, 248, 255),
            "height": 220,
            "boxes": [
                {
                    "name": "Offline Model Manager",
                    "sub": "model_manager.py",
                    "items": ["Ollama endpoint discovery", "Streaming pull (25/50/75%)", "Local model inventory", "Auto-persistence on reinstall"]
                },
                {
                    "name": "Resource Governor",
                    "sub": "governor.py (Independent)",
                    "items": ["1m/5m/15m CPU load tracking", "Free RAM & swap pressure", "is_safe_to_execute() check", "Graceful fallback without eBPF"]
                },
                {
                    "name": "Offline Voice Engine",
                    "sub": "voice_engine.py",
                    "items": ["Neural Edge-TTS (Primary)", "Windows SAPI / .NET (Natural)", "espeak-ng fallback", "256-entry LRU audio cache"]
                },
                {
                    "name": "Vector Memory & DB",
                    "sub": "vector_db.py",
                    "items": ["SemanticEmbedder: 256-d vector", "Zero-dependency tokenizer", "SQLite binary vector storage", "Cosine similarity local RAG"]
                }
            ]
        },
        {
            "title": "LAYER 7: OPERATING SYSTEM, KERNEL & HYPERVISOR BOUNDARY",
            "title_color": (139, 92, 246, 255),
            "height": 200,
            "boxes": [
                {
                    "name": "OS Runtimes",
                    "sub": "Linux / WSL2 / Windows",
                    "items": ["Debian / Ubuntu marrowai.deb", "WSL2 Linux environment", "Arch Linux execution target", "Multi-shell: bash, PowerShell"]
                },
                {
                    "name": "Kernel & Procfs",
                    "sub": "Telemetry Hooks",
                    "items": ["/proc/loadavg & meminfo reads", "/proc/net/route gateway detect", "cgroups v2 resource quotas", "Userspace privilege separation"]
                },
                {
                    "name": "Virtualization",
                    "sub": "QEMU / KVM / VirtualBox",
                    "items": ["/dev/kvm hardware accel", "QEMU headless VNC/SPICE", "VBoxManage automation", "Isolated sandbox testing"]
                }
            ]
        }
    ]

    render_svg_to_png_custom(
        hld_svg_path,
        hld_png_path,
        "MarrowAI — High-Level Architecture (HLD)",
        "Autonomous, Local-First Linux Workstation Assistant | System Topology & Component Pipeline",
        hld_layers
    )

    lld_layers = [
        {
            "title": "1. TYPED DATA CONTRACTS & INTERFACE SCHEMAS (interfaces.py)",
            "title_color": (56, 189, 248, 255),
            "height": 230,
            "boxes": [
                {
                    "name": "UserInput",
                    "sub": "Data Contract",
                    "items": ["text: str | None", "audio: bytes | None", "source: 'text'|'voice'", "metadata: dict[str, Any]"]
                },
                {
                    "name": "TaskPlan",
                    "sub": "Data Contract",
                    "items": ["id: str, intent: str", "steps: list[PlanStep]", "constraints: list[str]", "risk_level: 'low'|'med'|'high'"]
                },
                {
                    "name": "PlanStep",
                    "sub": "Data Contract",
                    "items": ["id: str, action_type: str", "description: str", "tool_name: str | None", "parameters: dict[str, Any]"]
                },
                {
                    "name": "SafetyDecision",
                    "sub": "Data Contract",
                    "items": ["decision: ALLOW|REVIEW|DENY", "reason: str", "confidence: float = 1.0", "requires_confirmation: bool"]
                },
                {
                    "name": "ExecutionResult",
                    "sub": "Data Contract",
                    "items": ["status: success|failed|blocked", "output: str, exit_code: int", "logs: list[str]", "warnings: list[str]"]
                }
            ]
        },
        {
            "title": "2. CORE COMPONENT CLASS ARCHITECTURE & METHOD SIGNATURES",
            "title_color": (99, 102, 241, 255),
            "height": 260,
            "boxes": [
                {
                    "name": "MarrowAssistant",
                    "sub": "assistant.py Facade",
                    "items": ["+ process(prompt, confirmed, password)", "+ execute_plan(plan: TaskPlan)", "+ check_telemetry() -> TelemetryData", "+ is_conversational(intent) -> bool"]
                },
                {
                    "name": "Planner & Safety",
                    "sub": "planner.py & safety.py",
                    "items": ["+ plan(prompt: str) -> TaskPlan", "+ evaluate(step: PlanStep) -> Decision", "+ classify_risk(action_type) -> str", "+ is_destructive(cmd_str) -> bool"]
                },
                {
                    "name": "ModelManager & Gov",
                    "sub": "model_manager.py / governor.py",
                    "items": ["+ download_model(name, cb, voice)", "+ list_local_models_detailed()", "+ get_telemetry() -> TelemetryData", "+ is_safe_to_execute() -> tuple"]
                },
                {
                    "name": "VoiceEngine & VectorDB",
                    "sub": "voice_engine.py / vector_db.py",
                    "items": ["+ synthesize_neural_audio() -> bytes", "+ speak(text: str) -> VoiceStatus", "+ SemanticEmbedder.encode(text) -> list", "+ similarity_search(query, k) -> list"]
                }
            ]
        },
        {
            "title": "3. INTERACTION SEQUENCE FLOW: PROMPT-TO-EXECUTION WITH SAFETY GATE",
            "title_color": (16, 185, 129, 255),
            "height": 240,
            "boxes": [
                {
                    "name": "1. Ingest & Plan",
                    "sub": "UI -> Assistant -> Planner",
                    "items": ["User submits prompt", "Assistant routes to Planner", "Planner creates TaskPlan", "Emits typed PlanSteps"]
                },
                {
                    "name": "2. Risk & Policy Gate",
                    "sub": "Assistant -> RiskClassifier",
                    "items": ["Evaluates action risk", "Checks policy rules", "HIGH risk -> requires_confirmation", "Password verified if sudo"]
                },
                {
                    "name": "3. Tool Dispatch",
                    "sub": "Assistant -> ToolRouter",
                    "items": ["Validates tool parameters", "Matches registered schema", "Checks timeout & governor", "Creates ToolCall payload"]
                },
                {
                    "name": "4. Execution & Audit",
                    "sub": "Executor -> OS -> AuditLog",
                    "items": ["Bounded subprocess exec", "Captures stdout/stderr", "Logs action to audit file", "Returns ExecutionResult"]
                }
            ]
        },
        {
            "title": "4. REAL-TIME MODEL STREAMING & NEURAL VOICE PIPELINES",
            "title_color": (245, 158, 11, 255),
            "height": 230,
            "boxes": [
                {
                    "name": "Model Pull Stream",
                    "sub": "SSE EventSource Pipeline",
                    "items": ["GET /api/pull_stream?model=...", "Ollama /api/pull stream:true", "Milestones: 25%, 50%, 75%, 100%", "Dropdown auto-updates"]
                },
                {
                    "name": "Neural Speech Flow",
                    "sub": "Edge-TTS Studio Pipeline",
                    "items": ["GET /api/tts?voice=...&text=...", "Edge-TTS communicates with Neerja", "Cached in _AUDIO_CACHE", "Web Speech fallback"]
                },
                {
                    "name": "Vector RAG Flow",
                    "sub": "256-d Semantic Search",
                    "items": ["SemanticEmbedder tokenizes text", "Computes normalized vector", "Cosine similarity in SQLite", "Augments prompt context"]
                }
            ]
        }
    ]

    render_svg_to_png_custom(
        lld_svg_path,
        lld_png_path,
        "MarrowAI — Low-Level Design (LLD)",
        "Class Architectures, Typed Data Contracts, Method Signatures & Interaction Sequences",
        lld_layers
    )

    print("All HLD and LLD SVG and PNG diagrams generated successfully!")


if __name__ == "__main__":
    main()
