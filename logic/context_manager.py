"""
Context Manager for GravityHook

Scans .agent/ directory and loads repository context including rules, workflows, and skills.
Provides structured access to project configuration for both Antigravity and OpenClaw.
"""

from pathlib import Path
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
import frontmatter
import json


class Rule(BaseModel):
    """Represents a rule from .agent/rules/"""
    name: str
    description: Optional[str] = None
    content: str
    file_path: Path
    metadata: Dict[str, Any] = Field(default_factory=dict)


class Workflow(BaseModel):
    """Represents a workflow from .agent/workflows/"""
    name: str
    description: Optional[str] = None
    steps: str
    file_path: Path
    metadata: Dict[str, Any] = Field(default_factory=dict)


class WorkspaceContext(BaseModel):
    """Complete workspace context loaded from .agent/ directory"""
    workspace_root: Path
    has_agent_dir: bool
    rules: List[Rule] = Field(default_factory=list)
    workflows: List[Workflow] = Field(default_factory=list)
    has_antigravity_skills: bool = False
    mission_state_path: Optional[Path] = None
    vibe_check_path: Optional[Path] = None

    class Config:
        arbitrary_types_allowed = True


def initialize_workspace(cwd: Optional[Path] = None) -> WorkspaceContext:
    """
    Scan workspace and load .agent/ configuration.
    
    Args:
        cwd: Current working directory. Defaults to Path.cwd()
    
    Returns:
        WorkspaceContext with loaded rules, workflows, and configuration
    
    Example:
        >>> context = initialize_workspace()
        >>> print(f"Found {len(context.rules)} rules")
        >>> for rule in context.rules:
        ...     print(f"  - {rule.name}")
    """
    if cwd is None:
        cwd = Path.cwd()
    else:
        cwd = Path(cwd)
    
    agent_dir = cwd / ".agent"
    has_agent = agent_dir.exists() and agent_dir.is_dir()
    
    context = WorkspaceContext(
        workspace_root=cwd,
        has_agent_dir=has_agent
    )
    
    if not has_agent:
        return context
    
    # Scan for rules
    rules_dir = agent_dir / "rules"
    if rules_dir.exists():
        context.rules = scan_agent_rules(rules_dir)
    
    # Scan for workflows
    workflows_dir = agent_dir / "workflows"
    if workflows_dir.exists():
        context.workflows = scan_workflows(workflows_dir)
    
    # Check for Antigravity-specific skills
    skills_dir = agent_dir / "skills"
    if skills_dir.exists():
        context.has_antigravity_skills = detect_antigravity_skills(skills_dir)
    
    # Check for MISSION_STATE.md
    mission_state = agent_dir / "MISSION_STATE.md"
    if mission_state.exists():
        context.mission_state_path = mission_state
    
    # Check for vibe_check.md
    vibe_check = agent_dir / "vibe_check.md"
    if vibe_check.exists():
        context.vibe_check_path = vibe_check
    
    return context


def scan_agent_rules(rules_dir: Path) -> List[Rule]:
    """
    Parse all .md files in .agent/rules/ directory.
    
    Supports both plain markdown and markdown with YAML frontmatter.
    """
    rules = []
    
    for rule_file in rules_dir.glob("*.md"):
        try:
            # Try parsing with frontmatter first
            with open(rule_file, 'r', encoding='utf-8') as f:
                post = frontmatter.load(f)
            
            rule = Rule(
                name=rule_file.stem,
                description=post.metadata.get('description'),
                content=post.content,
                file_path=rule_file,
                metadata=post.metadata
            )
            rules.append(rule)
        except Exception as e:
            # Fallback to plain text
            with open(rule_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            rule = Rule(
                name=rule_file.stem,
                content=content,
                file_path=rule_file
            )
            rules.append(rule)
    
    return rules


def scan_workflows(workflows_dir: Path) -> List[Workflow]:
    """
    Parse all .md files in .agent/workflows/ directory.
    
    Expected format:
    ---
    description: [short title]
    ---
    [workflow steps]
    """
    workflows = []
    
    for workflow_file in workflows_dir.glob("*.md"):
        try:
            with open(workflow_file, 'r', encoding='utf-8') as f:
                post = frontmatter.load(f)
            
            workflow = Workflow(
                name=workflow_file.stem,
                description=post.metadata.get('description'),
                steps=post.content,
                file_path=workflow_file,
                metadata=post.metadata
            )
            workflows.append(workflow)
        except Exception as e:
            # Fallback to plain text
            with open(workflow_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            workflow = Workflow(
                name=workflow_file.stem,
                steps=content,
                file_path=workflow_file
            )
            workflows.append(workflow)
    
    return workflows


def detect_antigravity_skills(skills_dir: Path) -> bool:
    """
    Check if .agent/skills/ contains Antigravity-specific skills.
    
    Looks for SKILL.md files which indicate Antigravity skill packages.
    """
    skill_files = list(skills_dir.glob("**/SKILL.md"))
    return len(skill_files) > 0


def print_context_summary(context: WorkspaceContext) -> str:
    """
    Generate human-readable summary of workspace context.
    
    Useful for OpenClaw to announce what it has detected.
    """
    lines = []
    lines.append("📋 GravityHook Context Scan Results")
    lines.append("=" * 50)
    lines.append(f"Workspace: {context.workspace_root}")
    
    if not context.has_agent_dir:
        lines.append("❌ No .agent/ directory found")
        lines.append("💡 Run install.sh to initialize GravityHook")
        return "\n".join(lines)
    
    lines.append("✅ .agent/ directory detected")
    
    if context.rules:
        lines.append(f"\n📜 Rules ({len(context.rules)}):")
        for rule in context.rules:
            desc = f" - {rule.description}" if rule.description else ""
            lines.append(f"  • {rule.name}{desc}")
    
    if context.workflows:
        lines.append(f"\n🔄 Workflows ({len(context.workflows)}):")
        for workflow in context.workflows:
            desc = f" - {workflow.description}" if workflow.description else ""
            lines.append(f"  • {workflow.name}{desc}")
    
    if context.has_antigravity_skills:
        lines.append("\n⚡ Antigravity Skills detected")
    
    if context.mission_state_path:
        lines.append(f"\n📊 Mission State: {context.mission_state_path.name}")
    
    if context.vibe_check_path:
        lines.append(f"✨ Vibe Check: {context.vibe_check_path.name}")
    
    return "\n".join(lines)


# Example usage for testing
if __name__ == "__main__":
    context = initialize_workspace()
    print(print_context_summary(context))
