"""
Mission Summarizer for GravityHook

Maintains MISSION_STATE.md as a living document that tracks:
- Current mission objectives
- Architecture snapshots
- Development log
- Technical debt and lessons learned
- Next action items

Enhanced with Git-aware summary generation that analyzes code changes
and extracts logical intent rather than just listing changed lines.
"""

from pathlib import Path
from typing import List, Optional, Dict, Tuple
from pydantic import BaseModel, Field
from datetime import datetime
import re
import subprocess


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


class GitChangeAnalysis(BaseModel):
    """Represents analyzed git changes with semantic meaning"""
    file_path: str
    change_type: str  # "added", "modified", "deleted", "renamed"
    intent: str  # Human-readable description of what changed and why
    added_lines: int = 0
    removed_lines: int = 0


class GitDiffSummary(BaseModel):
    """Summary of git diff analysis"""
    commit_hash: Optional[str] = None
    changes: List[GitChangeAnalysis] = Field(default_factory=list)
    summary: str  # Overall summary of the changeset


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


def analyze_git_diff(workspace_root: Path, commit_range: str = "HEAD") -> GitDiffSummary:
    """
    Analyze git diff and extract semantic meaning of changes.
    
    Args:
        workspace_root: Root directory of the git repository
        commit_range: Git commit range (e.g., "HEAD", "HEAD~1..HEAD", "main..feature")
    
    Returns:
        GitDiffSummary with analyzed changes and their intent
    
    Example:
        >>> summary = analyze_git_diff(Path("."), "HEAD~1..HEAD")
        >>> print(summary.summary)
        >>> for change in summary.changes:
        ...     print(f"  {change.file_path}: {change.intent}")
    """
    try:
        # Get commit hash if analyzing HEAD
        commit_hash = None
        if commit_range == "HEAD":
            result = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=workspace_root,
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                commit_hash = result.stdout.strip()[:7]  # Short hash
        
        # Get diff stats
        result = subprocess.run(
            ["git", "diff", "--numstat", commit_range],
            cwd=workspace_root,
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode != 0:
            return GitDiffSummary(
                summary="No git repository found or no changes detected"
            )
        
        changes = _parse_git_diff_output(result.stdout, workspace_root, commit_range)
        
        # Generate overall summary
        if not changes:
            overall_summary = "No changes detected"
        else:
            file_count = len(changes)
            added_total = sum(c.added_lines for c in changes)
            removed_total = sum(c.removed_lines for c in changes)
            
            change_types = {}
            for change in changes:
                change_types[change.change_type] = change_types.get(change.change_type, 0) + 1
            
            type_desc = ", ".join([f"{count} {type}" for type, count in change_types.items()])
            overall_summary = f"Modified {file_count} files ({type_desc}): +{added_total} -{removed_total} lines"
        
        return GitDiffSummary(
            commit_hash=commit_hash,
            changes=changes,
            summary=overall_summary
        )
    
    except subprocess.TimeoutExpired:
        return GitDiffSummary(summary="Git diff analysis timed out")
    except Exception as e:
        return GitDiffSummary(summary=f"Error analyzing git diff: {str(e)}")


def _parse_git_diff_output(diff_output: str, workspace_root: Path, commit_range: str) -> List[GitChangeAnalysis]:
    """Parse git diff --numstat output and infer intent for each file."""
    changes = []
    
    for line in diff_output.strip().split('\n'):
        if not line:
            continue
        
        parts = line.split('\t')
        if len(parts) != 3:
            continue
        
        added, removed, filepath = parts
        
        # Handle binary files
        if added == '-' or removed == '-':
            added_count = 0
            removed_count = 0
            change_type = "modified"
        else:
            added_count = int(added)
            removed_count = int(removed)
            
            # Infer change type
            if added_count > 0 and removed_count == 0:
                change_type = "added"
            elif added_count == 0 and removed_count > 0:
                change_type = "deleted"
            else:
                change_type = "modified"
        
        # Infer intent from file path and change pattern
        intent = _infer_change_intent(
            filepath,
            added_count,
            removed_count,
            change_type,
            workspace_root,
            commit_range
        )
        
        changes.append(GitChangeAnalysis(
            file_path=filepath,
            change_type=change_type,
            intent=intent,
            added_lines=added_count,
            removed_lines=removed_count
        ))
    
    return changes


def _infer_change_intent(
    filepath: str,
    added: int,
    removed: int,
    change_type: str,
    workspace_root: Path,
    commit_range: str
) -> str:
    """
    Infer the logical intent of a file change using heuristics.
    
    This is a simplified heuristic approach. For production use, consider:
    - Analyzing actual diff content (not just stats)
    - Using AST parsing for code files
    - ML-based commit message generation
    """
    filename = Path(filepath).name
    extension = Path(filepath).suffix
    
    # File type specific heuristics
    if extension in ['.md', '.txt', '.rst']:
        if change_type == "added":
            return f"Added documentation: {filename}"
        elif change_type == "deleted":
            return f"Removed documentation: {filename}"
        else:
            ratio = added / (removed + 1)  # Avoid division by zero
            if ratio > 2:
                return f"Expanded documentation in {filename}"
            elif ratio < 0.5:
                return f"Simplified documentation in {filename}"
            else:
                return f"Updated documentation in {filename}"
    
    elif extension in ['.py', '.js', '.ts', '.java', '.go', '.rs']:
        if change_type == "added":
            if 'test' in filepath.lower():
                return f"Added test file: {filename}"
            else:
                return f"Implemented new module: {filename}"
        elif change_type == "deleted":
            return f"Removed obsolete code: {filename}"
        else:
            # Try to get actual diff content for better analysis
            try:
                result = subprocess.run(
                    ["git", "diff", commit_range, "--", filepath],
                    cwd=workspace_root,
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                
                if result.returncode == 0:
                    diff_content = result.stdout.lower()
                    
                    # Heuristic analysis of diff content
                    if 'def ' in diff_content or 'function ' in diff_content or 'class ' in diff_content:
                        if added > removed * 1.5:
                            return f"Added new functionality to {filename}"
                        elif removed > added * 1.5:
                            return f"Refactored and simplified {filename}"
                        else:
                            return f"Modified logic in {filename}"
                    
                    if 'import ' in diff_content or 'from ' in diff_content:
                        return f"Updated dependencies in {filename}"
                    
                    if 'fix' in diff_content or 'bug' in diff_content:
                        return f"Fixed bug in {filename}"
            except:
                pass
            
            return f"Modified {filename}"
    
    elif extension in ['.json', '.yaml', '.yml', '.toml', '.ini']:
        if change_type == "added":
            return f"Added configuration file: {filename}"
        else:
            return f"Updated configuration in {filename}"
    
    elif extension in ['.html', '.css', '.scss']:
        if change_type == "added":
            return f"Created new UI component: {filename}"
        else:
            return f"Updated UI styling in {filename}"
    
    elif filename in ['requirements.txt', 'package.json', 'Cargo.toml', 'go.mod']:
        return f"Updated project dependencies"
    
    elif filename in ['README.md', 'CHANGELOG.md', 'LICENSE']:
        return f"Updated project {filename}"
    
    else:
        # Generic fallback
        if change_type == "added":
            return f"Added {filename}"
        elif change_type == "deleted":
            return f"Removed {filename}"
        else:
            return f"Modified {filename}"


def update_mission_log_with_git(
    mission_state_path: Path,
    task_summary: str,
    workspace_root: Optional[Path] = None,
    commit_range: str = "HEAD",
    vibe_check_passed: bool = False
) -> None:
    """
    Update MISSION_STATE.md with git-aware change analysis.
    
    This function automatically analyzes git diff and extracts the logical
    intent of code changes, creating a more meaningful development log entry.
    
    Args:
        mission_state_path: Path to MISSION_STATE.md file
        task_summary: Human-readable summary of what was accomplished
        workspace_root: Root of git repository (defaults to mission_state parent)
        commit_range: Git commit range to analyze (default: "HEAD")
        vibe_check_passed: Whether vibe check validation passed
    
    Example:
        >>> update_mission_log_with_git(
        ...     Path(".agent/MISSION_STATE.md"),
        ...     "Implemented user authentication",
        ...     workspace_root=Path("."),
        ...     commit_range="HEAD~1..HEAD"
        ... )
    """
    if workspace_root is None:
        workspace_root = mission_state_path.parent.parent
    
    # Analyze git changes
    git_summary = analyze_git_diff(workspace_root, commit_range)
    
    # Build change list from git analysis
    changes = []
    if git_summary.changes:
        changes.append(f"📊 {git_summary.summary}")
        changes.append("")
        
        for change in git_summary.changes:
            icon = {
                "added": "➕",
                "modified": "📝",
                "deleted": "❌",
                "renamed": "🔄"
            }.get(change.change_type, "•")
            
            changes.append(f"{icon} {change.intent}")
    
    # Use standard update_mission_log with git-enriched changes
    update_mission_log(
        mission_state_path,
        task_summary,
        changes if changes else None,
        vibe_check_passed
    )


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
