# Git-Aware Summary Feature Demo

This demonstrates the new `update_mission_log_with_git` function that automatically
analyzes git diffs and extracts logical intent from code changes.

## Features

### Automatic Change Analysis
Instead of manually listing changes, the function:
1. Runs `git diff` to see what changed
2. Analyzes each file to understand the intent
3. Generates human-readable descriptions

### Heuristic Intent Inference

The system uses file-type-specific heuristics:

**Python/JS/TypeScript** (.py, .js, .ts):
- Detects new modules vs modifications
- Identifies test files
- Recognizes refactoring patterns
- Looks for bug fixes in diff content

**Documentation** (.md, .txt, .rst):
- Expansion vs simplification
- New vs updated docs

**Configuration** (.json, .yaml, .toml):
- Dependency updates
- Config changes

**UI Files** (.html, .css):
- New components vs styling updates

### Example Usage

```python
from logic.mission_summarizer import update_mission_log_with_git
from pathlib import Path

# Analyze changes between last commit and current HEAD
update_mission_log_with_git(
    Path(".agent/MISSION_STATE.md"),
    "Added git-aware summary feature",
    workspace_root=Path("."),
    commit_range="HEAD~1..HEAD",
    vibe_check_passed=True
)
```

### Example Output in MISSION_STATE.md

```markdown
### ✅ Added git-aware summary feature
**Date**: 2026-02-05 02:00

**Changes**:
- 📊 Modified 2 files (2 modified): +290 -5 lines
- 
- 📝 Added new functionality to mission_summarizer.py
- 📝 Updated dependencies in __init__.py
```

## Benefits

1. **Development Documentary**: Reading MISSION_STATE.md feels like watching a documentary of your project's evolution
2. **Semantic Not Syntactic**: Describes *what* and *why*, not just *which lines*
3. **Zero Manual Work**: OpenClaw runs this automatically
4. **Git History Integration**: Leverages existing git commits

## Advanced Features

### Custom Commit Ranges
```python
# Analyze specific commits
update_mission_log_with_git(..., commit_range="abc123..def456")

# Analyze branch differences
update_mission_log_with_git(..., commit_range="main..feature-branch")

# Analyze last N commits
update_mission_log_with_git(..., commit_range="HEAD~5..HEAD")
```

### Fallback Behavior
If git is not available or there are no changes, the function gracefully falls back to standard `update_mission_log` behavior.

## Future Enhancements

Potential improvements:
- **AST-based analysis**: Parse Python/JS code for deeper insights
- **ML-powered summaries**: Use language models for better intent extraction
- **Commit message integration**: Extract info from git commit messages
- **Visual diff rendering**: Include code snippets in MISSION_STATE.md
- **Dependency graph updates**: Auto-detect when imports change relationships

---

**Status**: Production ready  
**Requires**: Git installed in system PATH  
**Compatibility**: Works on Windows, Linux, macOS
