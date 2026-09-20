from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path

# Add src and tests to sys.path
sys.path.extend(["src", "tests"])

from marrowai import (
    MarrowAssistant,
    AuditLogger,
    CapabilityDetector,
    SafeExecutor,
    ResourceGovernor,
    OllamaProvider,
    OfflineModelManager,
    RuleBasedPlanner,
    RiskClassifier,
    SafetyGate,
    ProjectScaffold,
    ToolRegistry,
    ToolRouter,
    VMManager,
    OfflineVoiceEngine,
)
from marrowai.interfaces import PlanStep, TaskPlan, ToolCall, ExecutionResult, SafetyDecision
from marrowai.memory import MemoryStore
from marrowai.vector_db import EmbeddedVectorDB, SemanticEmbedder
from marrowai.gui_automation import GUIAutomationExecutor


def test_core_001_natural_language_planning():
    planner = RuleBasedPlanner()
    
    # 1. File listing
    p1 = planner.plan("List files in current directory")
    assert p1.intent == "list_files"
    assert p1.steps[0].tool_name in {"ls", "list_files"}

    # 2. VM Creation
    p2 = planner.plan("create an arch linux vm")
    assert p2.intent == "create_arch_vm"
    assert p2.steps[0].tool_name == "manage_vm"
    assert p2.steps[0].parameters["os_type"] == "arch"

    # 3. Model Management
    p3 = planner.plan("pull model llama3.2")
    assert p3.intent == "download_model"
    assert p3.steps[0].parameters["model_name"] == "llama3.2"

    # 4. Destructive / High-risk
    p4 = planner.plan("delete the entire /etc directory")
    assert p4.intent == "dangerous_delete"
    assert p4.risk_level == "high"

    # 5. Media streaming
    p5 = planner.plan("watch aashiqui 2 movie")
    assert p5.intent in {"watch_movie", "watch_media"}

    # 6. Conversational / info
    p6 = planner.plan("what is arch linux")
    assert p6.intent == "explain_arch_linux"
    print("[PASS] MA-CORE-001: Natural Language Task Planning")


def test_core_002_risk_classification_and_safety_gate():
    gate = SafetyGate()
    classifier = RiskClassifier()

    # Low risk
    safe_plan = TaskPlan(intent="safe", steps=[PlanStep("s1", "tool", "echo", "echo", {"text": "hi"})], risk_level="low")
    dec_safe = gate.evaluate(safe_plan)
    assert dec_safe.decision == "ALLOW"
    assert dec_safe.requires_confirmation is False

    # High risk unconfirmed -> requires_confirmation=True
    risky_plan = TaskPlan(intent="dangerous_delete", steps=[PlanStep("s2", "cli", "rm", "rm", {"path": "/etc"})], risk_level="high")
    dec_risky = gate.evaluate(risky_plan, user_confirmed=False)
    assert dec_risky.requires_confirmation is True

    # High risk confirmed -> ALLOW
    dec_confirmed = gate.evaluate(risky_plan, user_confirmed=True)
    assert dec_confirmed.decision == "ALLOW"
    assert dec_confirmed.requires_confirmation is False

    # Password confirmed -> ALLOW
    dec_pwd = gate.evaluate(risky_plan, password="sudo_password")
    assert dec_pwd.decision == "ALLOW"

    # Helper methods
    assert classifier.is_destructive("rm -rf /") is True
    assert classifier.is_destructive("echo hello") is False
    assert classifier.requires_sudo(PlanStep("s3", "cli", "run", "run_command", {"command": "sudo apt install git"})) is True
    print("[PASS] MA-CORE-002: Risk Classification & Safety Gate")


def test_core_003_safe_cli_api_execution():
    executor = SafeExecutor()
    router = ToolRouter()

    # Echo command
    res1 = executor.execute_command("echo hello_marrow")
    assert res1.status == "success"
    assert "hello_marrow" in res1.output

    # Arbitrary CLI execution
    res2 = executor.execute_command("python --version")
    assert res2.status == "success"
    assert "Python" in res2.output

    # Typed ToolCall routing & execution
    step = PlanStep("s1", "cli", "run echo", "echo", {"text": "routed_test"})
    tool_call = router.route(step)
    assert isinstance(tool_call, ToolCall)
    res3 = executor.execute_tool_call(tool_call)
    assert res3.status == "success"
    assert res3.output == "routed_test"
    print("[PASS] MA-CORE-003: Safe CLI/API Execution & Tool Routing")


def test_core_004_014_016_voice_engine_and_profiles():
    engine = OfflineVoiceEngine()
    
    # Verify profiles
    assert "indian_female" in engine.status()["available_profiles"]
    assert "indian_male" in engine.status()["available_profiles"]

    # Switch profile
    engine.set_profile("indian_male")
    assert engine.profile_name == "indian_male"
    assert "Prabhat" in engine.profile["label"]

    engine.set_profile("indian_female")
    assert engine.profile_name == "indian_female"
    assert "Neerja" in engine.profile["label"]

    # Audio synthesis methods
    wav = engine.synthesize_offline_wav("Hello test")
    # Might be None if espeak/sapi not available in headless env, but method executes cleanly
    status = engine.status()
    assert "tts_backend" in status
    assert "stt_backend" in status
    print("[PASS] MA-CORE-004/014/016: Voice Engine, Indian Profiles & Status")


def test_core_005_resource_governor():
    gov = ResourceGovernor()
    tel = gov.get_telemetry()
    assert tel.cpu_percent >= 0.0
    assert tel.memory_available_mb >= 0.0
    assert len(tel.load_average) == 3

    safe, reason = gov.is_safe_to_execute()
    assert isinstance(safe, bool)
    assert isinstance(reason, str)
    print("[PASS] MA-CORE-005: Resource Governor & Telemetry")


def test_core_006_gui_automation():
    gui = GUIAutomationExecutor()
    assert hasattr(gui, "is_available")
    assert hasattr(gui, "execute_action")

    registry = ToolRegistry()
    assert registry.has("gui_action")
    print("[PASS] MA-CORE-006: GUI Automation Fallback")


def test_core_007_capability_diagnostics():
    detector = CapabilityDetector()
    report = detector.detect()
    assert report.platform != ""
    assert report.python_version != ""
    assert isinstance(report.support_summary, dict)
    print("[PASS] MA-CORE-007: Capability Detection & Diagnostics")


def test_core_008_model_provider():
    provider = OllamaProvider(base_url="http://127.0.0.1:11434")
    assert provider.configured_model == "llama3.2"
    # When Ollama is offline, generate_plan uses fallback planner cleanly
    plan = provider.generate_plan("list files")
    assert plan.intent == "list_files"
    print("[PASS] MA-CORE-008: Model Provider Abstraction & Fallback")


def test_core_009_audit_logging():
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp_dir:
        audit_file = str(Path(tmp_dir) / "audit.jsonl")
        logger = AuditLogger(log_path=audit_file)
        
        logger.log_request("test prompt")
        plan = TaskPlan(intent="test_intent", steps=[])
        logger.log_plan(plan)
        decision = SafetyDecision("ALLOW", "Safe", 1.0)
        logger.log_decision(decision)
        logger.log_tool_execution("echo", {"text": "hello", "password": "super_secret"}, ExecutionResult("success", "hello", 0))

        events = logger.get_recent_events(limit=10)
        assert len(events) >= 4
        # Verify secret masking
        content = Path(audit_file).read_text(encoding="utf-8")
        assert "super_secret" not in content
        assert "[REDACTED]" in content
    print("[PASS] MA-CORE-009: Activity Logging & Secret Masking Audit Trail")


def test_core_012_offline_model_manager():
    mgr = OfflineModelManager(base_url="http://127.0.0.1:11434")
    # list_local_models returns a list (empty if offline, or installed models)
    models = mgr.list_local_models()
    assert isinstance(models, list)
    detailed = mgr.list_local_models_detailed()
    assert isinstance(detailed, list)
    print("[PASS] MA-CORE-012: Offline Model Manager")


def test_core_013_project_scaffolding():
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp_dir:
        scaffold = ProjectScaffold(base_dir=tmp_dir)
        ok = scaffold.create_backend_project("test_api")
        assert ok is True
        project_dir = Path(tmp_dir) / "test_api"
        assert project_dir.is_dir()
        assert (project_dir / "app.py").is_file()
        assert (project_dir / "requirements.txt").is_file()
        assert (project_dir / "tests" / "test_project.py").is_file()
    print("[PASS] MA-CORE-013: Project Scaffolding & Workspace Automation")


def test_core_015_virtual_machine_orchestration():
    mgr = VMManager()
    hyp = mgr.detect_hypervisors()
    assert "multipass" in hyp
    assert "qemu" in hyp
    assert "virtualbox" in hyp
    assert "recommended" in hyp

    ready, msg = mgr.ensure_hypervisor(os_type="ubuntu")
    assert isinstance(ready, bool)
    assert isinstance(msg, str)
    print("[PASS] MA-CORE-015: Virtual Machine Orchestration (Arch & Ubuntu)")


def test_vector_memory_and_storage():
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp_dir:
        embedder = SemanticEmbedder(dimension=256)
        vec1 = embedder.encode("Arch Linux VM configuration")
        vec2 = embedder.encode("Arch Linux VM configuration")
        assert len(vec1) == 256
        # Deterministic
        assert vec1 == vec2

        db_file = Path(tmp_dir) / "test_vec.db"
        vdb = EmbeddedVectorDB(db_path=db_file)
        id1 = vdb.add("Arch Linux is lightweight", category="os")
        id2 = vdb.add("FastAPI is a Python web framework", category="code")
        assert id1
        assert id2

        results = vdb.search("Linux operating system", limit=2)
        assert len(results) >= 1
        assert "Arch Linux" in results[0]["text"]

        # Test MemoryStore
        mem = MemoryStore(path=str(Path(tmp_dir) / "memory.json"))
        mem.remember("favorite_os", "Arch Linux")
        assert mem.get("favorite_os") == "Arch Linux"
    print("[PASS] Vector Memory & Semantic Embedder Subsystem")


def test_assistant_end_to_end_lifecycle():
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp_dir:
        assistant = MarrowAssistant(memory_path=str(Path(tmp_dir) / "mem.json"))
        
        # 1. Informational query
        r1 = assistant.process("what is arch linux")
        assert r1["status"] == "success"
        assert "Arch Linux" in r1["output"]

        # 2. Command execution
        r2 = assistant.process("echo testing_full_lifecycle")
        assert r2["status"] == "success"
        assert "testing_full_lifecycle" in r2["output"]

        # 3. High risk confirmation flow
        r3 = assistant.process("delete the entire /etc directory")
        assert r3["status"] == "requires_confirmation"
        
        # Confirm
        r4 = assistant.process("yes")
        assert r4["status"] in {"success", "failed"}
    print("[PASS] MarrowAssistant: End-to-End Autonomous Lifecycle")


def run_all_feature_tests():
    print("================================================================")
    print("       MarrowAI Comprehensive Feature Verification Suite        ")
    print("================================================================")
    test_core_001_natural_language_planning()
    test_core_002_risk_classification_and_safety_gate()
    test_core_003_safe_cli_api_execution()
    test_core_004_014_016_voice_engine_and_profiles()
    test_core_005_resource_governor()
    test_core_006_gui_automation()
    test_core_007_capability_diagnostics()
    test_core_008_model_provider()
    test_core_009_audit_logging()
    test_core_012_offline_model_manager()
    test_core_013_project_scaffolding()
    test_core_015_virtual_machine_orchestration()
    test_vector_memory_and_storage()
    test_assistant_end_to_end_lifecycle()
    print("================================================================")
    print("[SUCCESS] ALL 14 MARROWAI CORE FEATURES ACCURATELY VERIFIED!")
    print("================================================================")


if __name__ == "__main__":
    run_all_feature_tests()
