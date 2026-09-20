from __future__ import annotations

from marrowai.planner import RuleBasedPlanner
from marrowai.assistant import MarrowAssistant
from marrowai.voice_engine import VOICE_PROFILES, OfflineVoiceEngine
from marrowai.model_manager import OfflineModelManager


def test_planner_watches_movie_aashiqui_2():
    planner = RuleBasedPlanner()
    plan = planner.plan("i want to watch aashqui 2 movie")
    assert plan.intent == "watch_movie"
    assert plan.risk_level == "low"
    assert len(plan.steps) >= 1
    step = plan.steps[0]
    assert step.tool_name == "desktop_action"
    assert step.parameters.get("action") == "open_url"
    assert "youtube.com/results?search_query=" in step.parameters.get("target", "")
    assert "aashqui+2+movie" in step.parameters.get("target", "")


def test_planner_where_can_i_find_movie():
    planner = RuleBasedPlanner()
    plan = planner.plan("where can i find interstellar movie")
    assert plan.intent == "watch_movie"
    assert plan.risk_level == "low"
    assert "interstellar" in plan.steps[0].parameters.get("target", "")


def test_planner_searches_web():
    planner = RuleBasedPlanner()
    plan = planner.plan("search google for python async tutorials")
    assert plan.intent == "search_web"
    assert plan.risk_level == "low"
    assert "google.com/search?q=" in plan.steps[0].parameters.get("target", "")
    assert "python" in plan.steps[0].parameters.get("target", "")


def test_planner_conversational_safe_fallback():
    planner = RuleBasedPlanner()
    plan = planner.plan("i want to know what you can do for me please")
    assert plan.intent == "general_question"
    assert plan.risk_level == "low"
    assert plan.steps[0].tool_name == "echo"
    assert "MarrowAI" in plan.steps[0].parameters.get("text", "")


def test_assistant_prior_plan_narration():
    assistant = MarrowAssistant()
    # Mock planning to rule-based directly for unit test speed
    plan = assistant.fallback_planner.plan("i want to watch aashqui 2 movie")
    narration = assistant._narrate_intent(plan.intent, plan.steps)
    assert "aashqui 2 movie" in narration
    assert "formulating" in narration.lower() or "planned" in narration.lower()


def test_voice_profiles_include_hindi_and_natural_voices():
    assert "indian_female" in VOICE_PROFILES
    assert "indian_male" in VOICE_PROFILES
    assert "hindi_female" in VOICE_PROFILES
    assert "hindi_male" in VOICE_PROFILES

    # Check authentic neural voices
    assert VOICE_PROFILES["indian_female"]["neural_voice"] == "en-IN-NeerjaNeural"
    assert VOICE_PROFILES["indian_male"]["neural_voice"] == "en-IN-PrabhatNeural"
    assert VOICE_PROFILES["hindi_female"]["neural_voice"] == "hi-IN-SwaraNeural"
    assert VOICE_PROFILES["hindi_male"]["neural_voice"] == "hi-IN-MadhurNeural"


def test_model_manager_detailed_listing():
    mgr = OfflineModelManager()
    # Ensure list_local_models_detailed returns a list (empty or populated depending on service)
    models = mgr.list_local_models_detailed()
    assert isinstance(models, list)
