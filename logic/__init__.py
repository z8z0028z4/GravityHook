"""
GravityHook Logic Package

Core utilities for OpenClaw-Antigravity compatibility layer.
Provides context management, mission summarization, and verification tools.
"""

__version__ = "0.1.0"

from .context_manager import initialize_workspace, WorkspaceContext
from .mission_summarizer import update_mission_log, MissionState
from .vibe_checker import perform_vibe_check, CheckResult

__all__ = [
    "initialize_workspace",
    "WorkspaceContext",
    "update_mission_log",
    "MissionState",
    "perform_vibe_check",
    "CheckResult",
]
