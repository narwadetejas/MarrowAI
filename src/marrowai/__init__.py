"""MarrowAI core package."""

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

