"""
Mission Summarizer for GravityHook

Maintains MISSION_STATE.md as a living document that tracks:
- Current mission objectives
- Architecture snapshots
- Development log
- Technical debt and lessons learned
- Next action items
"""

from pathlib import Path
from typing import List, Optional, Dict
from pydantic import BaseModel, Field
from datetime import datetime
import re


class ArchitectureComponent(BaseModel):
    """Represents a component in the system architecture"""
    name: str
    description: str
    dependencies: List[str] = Field(default_factory=list)


class TechnicalDebtItem(BaseModel):
    """Represents a known issue or lesson learned"""
    title: str
    description: str
    context: Optional[str] = None
    timestamp: str
    severity: str = "medium"  # low, medium, high


class DevelopmentLogEntry(BaseModel):
    """Represents a completed task or milestone"""
    title: str
    description: str
    timestamp: str
    vibe_check_passed: bool = False


class MissionState(BaseModel):
    """Complete mission state representation"""
    current_mission: str
    architecture_components: List[ArchitectureComponent] = Field(default_factory=list)
    development_log: List[DevelopmentLogEntry] = Field(default_factory=list)
    technical_debt: List[TechnicalDebtItem] = Field(default_factory=list)
    next_actions: List[str] = Field(default_factory=list)


def update_mission_log(
    mission_state_path: Path,
    task_summary: str,
    changes: Optional[List[str]] = None,
    vibe_check_passed: bool = False
) -> None:
    """
    Update MISSION_STATE.md with new development log entry.
    
    Args:
        mission_state_path: Path to MISSION_STATE.md file
        task_summary: Human-readable summary of what was accomplished
        changes: List of specific changes made
        vibe_check_passed: Whether vibe check validation passed
    
    Example:
        >>> update_mission_log(
        ...     Path(".agent/MISSION_STATE.md"),
        ...     "Implemented user authentication system",
        ...     ["Added JWT token generation", "Created login endpoint"],
        ...     vibe_check_passed=True
        ... )
    """
    if not mission_state_path.exists():
        # Create new MISSION_STATE.md from template
        _create_initial_mission_state(mission_state_path)
    
    # Read existing content
    with open(mission_state_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Create new log entry
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    status_icon = "✅" if vibe_check_passed else "📝"
    
    log_entry = f"\n### {status_icon} {task_summary}\n"
    log_entry += f"**Date**: {timestamp}\n\n"
    
    if changes:
        log_entry += "**Changes**:\n"
        for change in changes:
            log_entry += f"- {change}\n"
        log_entry += "\n"
    
    # Find and update the Development Log section
    dev_log_pattern = r'(## \[Development Log\].*?)\n((?:###.*?\n(?:.*?\n)*?)+|\n)'
    
    if re.search(dev_log_pattern, content, re.MULTILINE | re.DOTALL):
        # Append to existing dev log
        content = re.sub(
            dev_log_pattern,
            r'\1\n' + log_entry + r'\2',
            content,
            count=1,
            flags=re.MULTILINE | re.DOTALL
        )
    else:
        # Add Development Log section if missing
        content += f"\n## [Development Log]\n{log_entry}"
    
    # Write updated content
    with open(mission_state_path, 'w', encoding='utf-8') as f:
        f.write(content)


def add_technical_debt(
    mission_state_path: Path,
    issue: str,
    context: str,
    severity: str = "medium"
) -> None:
    """
    Record a technical debt item or lesson learned.
    
    Args:
        mission_state_path: Path to MISSION_STATE.md
        issue: Title/summary of the issue
        context: Detailed explanation or lesson learned
        severity: low, medium, or high
    """
    if not mission_state_path.exists():
        _create_initial_mission_state(mission_state_path)
    
    with open(mission_state_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    timestamp = datetime.now().strftime("%Y-%m-%d")
    severity_icons = {"low": "ℹ️", "medium": "⚠️", "high": "🚨"}
    icon = severity_icons.get(severity, "⚠️")
    
    debt_entry = f"\n### {icon} {issue}\n"
    debt_entry += f"**Date**: {timestamp} | **Severity**: {severity}\n\n"
    debt_entry += f"{context}\n\n"
    
    # Find and update Technical Debt section
    debt_pattern = r'(## \[Technical Debt & Pitfalls\].*?)\n((?:###.*?\n(?:.*?\n)*?)+|\n)'
    
    if re.search(debt_pattern, content, re.MULTILINE | re.DOTALL):
        content = re.sub(
            debt_pattern,
            r'\1\n' + debt_entry + r'\2',
            content,
            count=1,
            flags=re.MULTILINE | re.DOTALL
        )
    else:
        content += f"\n## [Technical Debt & Pitfalls]\n{debt_entry}"
    
    with open(mission_state_path, 'w', encoding='utf-8') as f:
        f.write(content)


def sync_architecture_snapshot(
    mission_state_path: Path,
    components: List[Dict[str, any]]
) -> None:
    """
    Update the architecture snapshot section.
    
    Args:
        mission_state_path: Path to MISSION_STATE.md
        components: List of component dictionaries with keys: name, description, dependencies
    
    Example:
        >>> sync_architecture_snapshot(
        ...     Path(".agent/MISSION_STATE.md"),
        ...     [
        ...         {"name": "API Layer", "description": "FastAPI REST endpoints", "dependencies": ["Database"]},
        ...         {"name": "Database", "description": "PostgreSQL with SQLAlchemy", "dependencies": []}
        ...     ]
        ... )
    """
    if not mission_state_path.exists():
        _create_initial_mission_state(mission_state_path)
    
    with open(mission_state_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Build architecture section
    arch_content = "\n## [Architecture Snapshots]\n\n"
    
    for comp in components:
        arch_content += f"### {comp['name']}\n"
        arch_content += f"{comp['description']}\n\n"
        
        if comp.get('dependencies'):
            arch_content += "**Dependencies**: "
            arch_content += ", ".join([f"`{dep}`" for dep in comp['dependencies']])
            arch_content += "\n\n"
    
    # Replace architecture section
    arch_pattern = r'## \[Architecture Snapshots\].*?(?=\n## |\Z)'
    
    if re.search(arch_pattern, content, re.MULTILINE | re.DOTALL):
        content = re.sub(
            arch_pattern,
            arch_content.strip(),
            content,
            count=1,
            flags=re.MULTILINE | re.DOTALL
        )
    else:
        # Insert after Current Mission
        content = re.sub(
            r'(## \[Current Mission\].*?(?=\n## |\Z))',
            r'\1\n\n' + arch_content.strip(),
            content,
            count=1,
            flags=re.MULTILINE | re.DOTALL
        )
    
    with open(mission_state_path, 'w', encoding='utf-8') as f:
        f.write(content)


def suggest_next_actions(
    mission_state_path: Path,
    recommendations: List[str]
) -> None:
    """
    Update the Next Action Items section.
    
    Args:
        mission_state_path: Path to MISSION_STATE.md
        recommendations: List of suggested next steps
    """
    if not mission_state_path.exists():
        _create_initial_mission_state(mission_state_path)
    
    with open(mission_state_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Build next actions section
    actions_content = "\n## [Next Action Items]\n\n"
    for i, action in enumerate(recommendations, 1):
        actions_content += f"{i}. {action}\n"
    
    # Replace next actions section
    actions_pattern = r'## \[Next Action Items\].*?(?=\n## |\Z)'
    
    if re.search(actions_pattern, content, re.MULTILINE | re.DOTALL):
        content = re.sub(
            actions_pattern,
            actions_content.strip(),
            content,
            count=1,
            flags=re.MULTILINE | re.DOTALL
        )
    else:
        content += "\n" + actions_content
    
    with open(mission_state_path, 'w', encoding='utf-8') as f:
        f.write(content)


def _create_initial_mission_state(mission_state_path: Path) -> None:
    """Create initial MISSION_STATE.md from template."""
    template = """# Mission State

## [Current Mission]

_Define the current high-priority development goal here._

## [Architecture Snapshots]

_AI maintains module dependency graph and tech stack._

## [Development Log]

_AI appends completed features with timestamps._

## [Technical Debt & Pitfalls]

_AI records failed attempts and pending optimizations._

## [Next Action Items]

_AI suggests next steps based on current state._
"""
    
    mission_state_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(mission_state_path, 'w', encoding='utf-8') as f:
        f.write(template)


# Example usage
if __name__ == "__main__":
    # Test creating and updating MISSION_STATE.md
    test_path = Path("test_MISSION_STATE.md")
    
    update_mission_log(
        test_path,
        "Implemented context_manager.py",
        ["Added WorkspaceContext Pydantic model", "Scans .agent/ directory"],
        vibe_check_passed=True
    )
    
    add_technical_debt(
        test_path,
        "Async file I/O not implemented",
        "Currently using synchronous file reading. Consider using aiofiles for better performance.",
        severity="low"
    )
    
    print(f"Created test file: {test_path}")
