from __future__ import annotations

from marrowai.voice_engine import OfflineVoiceEngine, VOICE_PROFILES


def test_indian_voice_profiles_defined():
    assert "indian_female" in VOICE_PROFILES
    assert "indian_male" in VOICE_PROFILES
    assert VOICE_PROFILES["indian_female"]["espeak_voice"] == "en-in+f2"
    assert VOICE_PROFILES["indian_male"]["espeak_voice"] == "en-in+m3"
    assert VOICE_PROFILES["indian_female"]["label"] == "Indian English (Female)"
    assert VOICE_PROFILES["indian_male"]["label"] == "Indian English (Male)"


def test_voice_engine_switches_profile():
    engine = OfflineVoiceEngine(profile="indian_female")
    assert engine.profile_name == "indian_female"
    assert engine.speed == 150
    assert engine.pitch == 55

    engine.set_profile("indian_male")
    assert engine.profile_name == "indian_male"
    assert engine.speed == 145
    assert engine.pitch == 42


def test_voice_engine_speaks_with_profile():
    engine = OfflineVoiceEngine(profile="indian_female")
    res = engine.speak("Namaste, I am MarrowAI.")
    assert res is not None
    assert res.ok is True or res.engine == "fallback"
    assert res.profile == "indian_female"


def test_voice_engine_status_reports_profile():
    engine = OfflineVoiceEngine(profile="indian_male")
    status = engine.status()
    assert status["active_profile"] == "indian_male"
    assert status["profile_label"] == "Indian English (Male)"
    assert "indian_female" in status["available_profiles"]


def test_assistant_on_narration_callback():
    from marrowai.assistant import MarrowAssistant

    narrations_received = []
    assistant = MarrowAssistant()
    res = assistant.process("create an arch linux vm", on_narration=lambda msg: narrations_received.append(msg))
    assert res is not None
    assert len(narrations_received) == 1
    assert "Arch Linux" in narrations_received[0]


def test_planner_handles_informational_questions():
    from marrowai.planner import RuleBasedPlanner

    planner = RuleBasedPlanner()
    plan_arch = planner.plan("what is arch linux?")
    assert plan_arch.intent == "explain_arch_linux"
    assert plan_arch.steps[0].tool_name == "echo"
    assert "Arch Linux" in plan_arch.steps[0].parameters["text"]

    plan_voice = planner.plan("what voice profiles do you have?")
    assert plan_voice.intent == "voice_info"
    assert plan_voice.steps[0].tool_name == "echo"
    assert "Indian English" in plan_voice.steps[0].parameters["text"]


def test_interactive_session_voice_profile_init():
    from marrowai.interactive import InteractiveSession

    session_male = InteractiveSession(voice_profile="male")
    assert session_male.voice_engine.profile_name == "indian_male"

    session_female = InteractiveSession(voice_profile="female")
    assert session_female.voice_engine.profile_name == "indian_female"


def test_voice_engine_neural_voice_profiles():
    assert "neural_voice" in VOICE_PROFILES["indian_female"]
    assert "neural_voice" in VOICE_PROFILES["indian_male"]
    assert "Neerja" in VOICE_PROFILES["indian_female"]["neural_voice"]
    assert "Prabhat" in VOICE_PROFILES["indian_male"]["neural_voice"]


def test_voice_engine_neural_synthesis_empty_or_whitespace():
    engine = OfflineVoiceEngine()
    assert engine.synthesize_neural_audio("") is None
    assert engine.synthesize_neural_audio("   ") is None


def test_voice_engine_status_reports_neural_fields():
    engine = OfflineVoiceEngine()
    status = engine.status()
    assert "neural_tts_active" in status
    assert "neural_voice" in status
    assert "offline_backend" in status


def test_planner_handles_extended_interactive_questions():
    from marrowai.planner import RuleBasedPlanner

    planner = RuleBasedPlanner()
    plan_vm = planner.plan("what is a virtual machine?")
    assert plan_vm.intent == "explain_vm"
    assert "virtual machine" in plan_vm.steps[0].parameters["text"].lower()

    plan_model = planner.plan("which model do you recommend?")
    assert plan_model.intent == "explain_models"
    assert "llama3.2" in plan_model.steps[0].parameters["text"]

    plan_greeting = planner.plan("namaste")
    assert plan_greeting.intent == "greeting"
    assert "Namaste" in plan_greeting.steps[0].parameters["text"]

    plan_general = planner.plan("why should I use Linux?")
    assert plan_general.intent == "general_question"
    assert plan_general.steps[0].tool_name == "echo"


def test_assistant_speaks_interactive_answers_to_questions():
    from marrowai.assistant import MarrowAssistant

    spoken_narrations = []
    assistant = MarrowAssistant()
    res = assistant.process("what is a virtual machine?", on_narration=lambda msg: spoken_narrations.append(msg))
    assert res["status"] == "success"
    assert len(spoken_narrations) == 1
    assert "virtual machine" in spoken_narrations[0].lower()



