"""MarrowAI core package."""

import glob
import os
import sys
from pathlib import Path

# Automatically inject local virtual environment site-packages into sys.path if available
for candidate_dir in [
    Path(__file__).resolve().parents[2] / ".venv",
    Path("/home/tejas/Projects/MarrowAI/.venv"),
]:
    if candidate_dir.is_dir():
        for sp in glob.glob(str(candidate_dir / "lib" / "python*" / "site-packages")):
            if sp not in sys.path:
                sys.path.insert(0, sp)

from .assistant import MarrowAssistant
from .audit import AuditLogger
from .config import get_config
from .diagnostics import CapabilityDetector
from .executor import SafeExecutor
from .governor import ResourceGovernor
from .model import OllamaProvider
from .model_manager import OfflineModelManager
from .planner import RuleBasedPlanner
from .safety import RiskClassifier, SafetyGate
from .scaffold import ProjectScaffold
from .tools import ToolRegistry, ToolRouter
from .vm_manager import VMManager
from .voice_engine import OfflineVoiceEngine

__all__ = [
    "__version__",
    "MarrowAssistant",
    "AuditLogger",
    "get_config",
    "CapabilityDetector",
    "SafeExecutor",
    "ResourceGovernor",
    "OllamaProvider",
    "OfflineModelManager",
    "RuleBasedPlanner",
    "RiskClassifier",
    "SafetyGate",
    "ProjectScaffold",
    "ToolRegistry",
    "ToolRouter",
    "VMManager",
    "OfflineVoiceEngine",
]
__version__ = "0.2.0"

