# gravityhook: Lead Engineer Skill Pack

**Version**: 0.1.0  
**Description**: Equips OpenClaw with repository awareness and a long-term development log, optimized for co-working with Agent IDEs like Antigravity.

---

## 🎯 Purpose

GravityHook provides OpenClaw with:
1. **Rule Awareness**: Distinguishes between universal **Global Rules** and repository **Local Rules**.
2. **Development Memory**: Automatically maintains `MISSION_STATE.md` across sessions.
3. **Automated Verification**: Executes `vibe_check.md` validation flows.
4. **Impact Awareness**: Basic structural analysis for Python/Pydantic models.

This skill pack creates a **collaboration bridge** between OpenClaw and specialized Agent IDEs (like Antigravity), ensuring consistent coding standards and persistent project knowledge.

---

## 🛠️ Available Tools

### 1. `scan_repo_context()`
**Module**: `logic.context_manager`  
**Function**: `initialize_workspace(cwd: Path) -> WorkspaceContext`

Scans `.agent/` directory and loads all rules, workflows, and skills into session context.

**Returns**:
- List of rules from `.agent/rules/`
- List of workflows from `.agent/workflows/`
- Detection of Antigravity-specific skills
- Paths to MISSION_STATE.md and vibe_check.md

**When to use**:
- At the start of every new session
- When user mentions "reload context" or "refresh rules"
- After significant changes to `.agent/` directory

**Example**:
```python
from logic.context_manager import initialize_workspace, print_context_summary

context = initialize_workspace()
print(print_context_summary(context))

# Output:
# 📋 GravityHook Context Scan Results
# ==================================================
# Workspace: /path/to/project
# ✅ .agent/ directory detected
# 
# 📜 Rules (2):
#   • project_rules - Development standards and principles
#   • api_guidelines - REST API design conventions
```

---

### 2. `sync_mission_state()` / `sync_mission_state_with_git()`
**Module**: `logic.mission_summarizer`  
**Functions**: 
- `update_mission_log(mission_state_path, task_summary, changes, vibe_check_passed)`
- `update_mission_log_with_git(mission_state_path, task_summary, workspace_root, commit_range, vibe_check_passed)` ⭐ **NEW**

Updates `MISSION_STATE.md` with latest accomplishments and architectural changes.

**Standard Mode** - Manual change listing:
```python
update_mission_log(
    Path(".agent/MISSION_STATE.md"),
    "Implemented user authentication",
    ["Added JWT generation", "Created login endpoint"],
    vibe_check_passed=True
)
```

**Git-Aware Mode** ⭐ - Automatic change analysis from git diff:
```python
update_mission_log_with_git(
    Path(".agent/MISSION_STATE.md"),
    "Implemented user authentication",
    workspace_root=Path("."),
    commit_range="HEAD~1..HEAD",  # Analyze last commit
    vibe_check_passed=True
)
```

**Output Example**:
```markdown
### ✅ Implemented user authentication
**Date**: 2026-02-05 02:00

**Changes**:
- 📊 Modified 5 files (3 modified, 2 added): +145 -12 lines
- 
- 📝 Added new functionality to auth.py
- ➕ Implemented new module: jwt_handler.py
- 📝 Modified logic in user_model.py
- ➕ Added test file: test_auth.py
- 📝 Updated configuration in config.yaml
```

**When to use Git-Aware Mode**:
- When changes are already committed to git
- To create a "development documentary" style log
- To automatically extract logical intent from code changes
- For human engineers to quickly understand what changed and why

**Parameters**:
- `mission_state_path`: Path to MISSION_STATE.md (usually `.agent/MISSION_STATE.md`)
- `task_summary`: Human-readable summary of what was accomplished
- `workspace_root`: Root of git repository (defaults to mission_state parent)
- `commit_range`: Git commit range (e.g., "HEAD", "HEAD~1..HEAD", "main..feature")
- `vibe_check_passed`: Boolean indicating if verification passed

**When to use**:
- After completing any significant task
- After passing vibe_check verification
- When switching between major development phases

**Additional Functions**:
- `add_technical_debt(path, issue, context, severity)` - Record lessons learned
- `sync_architecture_snapshot(path, components)` - Update architecture diagram
- `suggest_next_actions(path, recommendations)` - Populate future roadmap

---

### 3. `perform_vibe_check()`
**Module**: `logic.vibe_checker`  
**Function**: `perform_vibe_check(vibe_check_path, auto_run=False) -> CheckResult`

Executes automated verification checklist from `.agent/vibe_check.md`.

**Parameters**:
- `vibe_check_path`: Path to vibe_check.md
- `auto_run`: If True, automatically execute command checks

**Returns**:
- `CheckResult` with pass/fail status of all checks
- Detailed breakdown of which checks passed/failed

**When to use**:
- After code changes, before marking task as complete
- Before committing to version control
- As part of CI/CD pipeline

**Example**:
```python
from logic.vibe_checker import perform_vibe_check, print_check_result
from pathlib import Path

result = perform_vibe_check(Path(".agent/vibe_check.md"), auto_run=True)
print(print_check_result(result))

# Output:
# ✨ Vibe Check Results
# ==================================================
# Total: 8 | ✅ Passed: 6 | ❌ Failed: 1 | ⏭️ Skipped: 1
# 
# ✅ All unit tests pass
# ✅ File exists: requirements.txt
# ❌ Code coverage is at least 80%
# ⏸️ Code follows async-first principles (manual review)

if result.all_passed:
    update_mission_log(..., vibe_check_passed=True)
else:
    add_technical_debt(..., "Vibe check failed - review items")
```

---

### 4. `analyze_impact()` *(Optional)*
**Module**: `logic.impact_analyzer`  
**Function**: `analyze_impact(file_path, workspace_root, proposed_changes) -> ImpactReport`

Analyzes structural impact before making code changes, especially for Pydantic models.

**When to use**:
- Before modifying core data models
- When refactoring shared utilities
- To predict downstream effects of API changes

**Example**:
```python
from logic.impact_analyzer import analyze_impact, print_impact_report
from pathlib import Path

report = analyze_impact(
    Path("backend/models/user.py"),
    Path("."),
    "Changing User.email from str to EmailStr"
)

print(print_impact_report(report))
# Shows which models are affected and where they're used
```

---

## ⚙️ Execution Priority

OpenClaw should follow this workflow:

### On Session Start
1. **Always** execute `scan_repo_context()`
2. Announce detected rules and workflows
3. Check if MISSION_STATE.md exists and read current mission

### Before Responding to User
1. Check if `.agent/rules/` contains project-specific rules
2. Filter proposed changes through rule constraints
3. Reference rules when explaining design decisions

### After Task Completion
1. Execute `perform_vibe_check()` if applicable
2. Execute `sync_mission_state()` with task summary
3. Update `[Next Action Items]` based on roadmap

### Before Closing Task
1. Verify MISSION_STATE.md is up-to-date
2. Ensure all changes are documented
3. Commit changes with meaningful message

---

## 📋 Integration Notes

### Version Control
- MISSION_STATE.md is **version-controlled** with Git
- Track evolution of project goals via Git history
- Use `git diff MISSION_STATE.md` to see decision changes

### Human Collaboration
- Human engineers can **manually edit** any section of MISSION_STATE.md
- AI should preserve human edits when updating
- Use MISSION_STATE.md as handoff document between sessions

### Cross-System Communication
- Antigravity can read MISSION_STATE.md to understand OpenClaw's work
- OpenClaw can read Antigravity's task.md and implementation_plan.md
- Both systems benefit from shared context in `.agent/`

### Failure Handling
- Failed vibe checks should be logged in `[Technical Debt]` section
- Record error context to prevent future repetition
- Use failures as learning opportunities

---

## 🚀 Quick Start for OpenClaw

```python
from logic.context_manager import initialize_workspace, print_context_summary
from logic.mission_summarizer import update_mission_log
from logic.vibe_checker import perform_vibe_check
from pathlib import Path

# Step 1: Load context
context = initialize_workspace()
print(print_context_summary(context))

# Step 2: Do work...
# (implement features, write code, etc.)

# Step 3: Verify work
if context.vibe_check_path:
    result = perform_vibe_check(context.vibe_check_path, auto_run=True)
    vibe_passed = result.all_passed
else:
    vibe_passed = False  # No vibe check available

# Step 4: Update mission state
if context.mission_state_path:
    update_mission_log(
        context.mission_state_path,
        "Task completed successfully",
        ["Change 1", "Change 2"],
        vibe_check_passed=vibe_passed
    )
```

---

## 📦 Installation

See main README.md for installation instructions. Use `install.sh` or `install.bat` to set up `.agent/` structure in target projects.

---

## 🤝 Contributing

This is a living skill pack. Suggested improvements:
- Add support for more verification types in vibe_checker
- Implement automated architecture diagram generation
- Create visual dashboard for mission state
- Add integration with project management tools

---

**Created by**: Antigravity & Human Collaboration  
**License**: MIT  
**Repository**: https://github.com/your-username/gravityhook
