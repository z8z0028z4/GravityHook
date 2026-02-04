# GravityHook 🪝

**A compatibility layer between Antigravity and OpenClaw AI systems**

GravityHook enables seamless collaboration between different AI coding assistants by providing:
- 📋 **Persistent Context Management**: Automatically scan and load project rules
- 🧠 **Long-Term Memory**: Maintain mission state across sessions
- ✅ **Automated Verification**: Execute validation checklists
- 🔍 **Structural Impact Analysis**: Predict effects of code changes

---

## 🎯 Why GravityHook?

When working with multiple AI systems (like Antigravity and OpenClaw), keeping them synchronized is challenging:
- Context resets between sessions
- Technical decisions get lost in conversation history
- No shared understanding of project goals and architecture

**GravityHook solves this** by creating a shared `.agent/` directory structure that both systems can read and update, ensuring continuous knowledge transfer.

---

## 📦 Installation

### For New Projects

1. Clone this repository:
```bash
git clone https://github.com/z8z0028z4/GravityHook.git
cd GravityHook
```

2. Run the installation script in your target project:

**Windows (PowerShell)**:
```powershell
.\install.bat C:\path\to\your\project
```

**Linux/macOS (Bash)**:
```bash
./install.sh /path/to/your/project
```

This will:
- Create `.agent/` directory in your project
- Copy templates (MISSION_STATE.md, vibe_check.md, claw_rules.md)
- Set up directory structure

### For Existing Projects

If your project already has a `.agent/` directory (e.g., Antigravity skills), GravityHook will integrate seamlessly:

```bash
cp templates/* /your/project/.agent/
```

---

## 🛠️ Usage

### For OpenClaw

Follow the [SKILL_MANIFEST.md](SKILL_MANIFEST.md) for detailed instructions. Quick start:

```python
from logic.context_manager import initialize_workspace
from logic.mission_summarizer import update_mission_log, update_mission_log_with_git
from logic.vibe_checker import perform_vibe_check

# Load repository context
context = initialize_workspace()

# After completing work (manual mode)
update_mission_log(
    context.mission_state_path,
    "Implemented feature X",
    ["Added Y", "Fixed Z"],
    vibe_check_passed=True
)

# After completing work (git-aware mode) ⭐ NEW
update_mission_log_with_git(
    context.mission_state_path,
    "Implemented feature X",
    workspace_root=Path("."),
    commit_range="HEAD~1..HEAD",  # Analyzes git diff automatically
    vibe_check_passed=True
)
```

### For Antigravity

Antigravity can read the same files to understand project state:

1. Read `MISSION_STATE.md` to see current objectives and progress
2. Read `claw_rules.md` to understand project constraints
3. Update `MISSION_STATE.md` manually or via Python utilities

### For Human Engineers

Use `MISSION_STATE.md` as your **project journal**:
- Quick reference for "what did we do last week?"
- Handoff document between sessions
- Technical decision log

---

## 📂 Project Structure

```
gravityhook/
├── core_rules/
│   └── project_rules.md       # Global development guidelines (template)
├── logic/
│   ├── __init__.py
│   ├── context_manager.py     # Scans .agent/ directory
│   ├── mission_summarizer.py  # Maintains MISSION_STATE.md
│   ├── vibe_checker.py        # Executes verification checklist
│   └── impact_analyzer.py     # (Optional) Analyzes structural impact
├── templates/
│   ├── MISSION_STATE.md       # Mission tracking template
│   ├── claw_rules.md          # Repository rules template
│   └── vibe_check.md          # Verification checklist template
├── tests/                     # Unit tests (to be implemented)
├── .gitignore
├── README.md
├── SKILL_MANIFEST.md          # OpenClaw skill definition
├── requirements.txt
├── install.sh                 # Installation script (Linux/macOS)
└── install.bat                # Installation script (Windows)
```

---

## 🔧 Key Features

### 1. Context Management (`context_manager.py`)

Automatically scans `.agent/` and loads:
- Project rules from `.agent/rules/`
- Workflows from `.agent/workflows/`
- Mission state from `.agent/MISSION_STATE.md`

```python
context = initialize_workspace()
print(f"Found {len(context.rules)} rules")
print(f"Current mission: {context.mission_state_path}")
```

### 2. Mission Summarization (`mission_summarizer.py`)

Maintains a living document of:
- **Current Mission**: High-priority development goals
- **Architecture Snapshots**: Module dependencies and tech stack
- **Development Log**: Completed features with timestamps
- **Technical Debt**: Lessons learned and pending optimizations
- **Next Actions**: Suggested next steps

**⭐ Git-Aware Summary** (NEW):
```python
update_mission_log_with_git(
    Path(".agent/MISSION_STATE.md"),
    "Refactored authentication",
    workspace_root=Path("."),
    commit_range="HEAD~1..HEAD"
)
```

Automatically analyzes `git diff` and extracts **semantic intent** of changes:
- "Added new functionality to auth.py" (not just "+50 lines")
- "Refactored and simplified user_model.py"
- "Updated project dependencies"

**Result**: Reading MISSION_STATE.md feels like watching a **development documentary** 🎬

### 3. Vibe Checker (`vibe_checker.py`)

Parses `vibe_check.md` and executes automated checks:
- Command execution (e.g., `pytest`)
- File existence checks
- Manual verification items

```python
result = perform_vibe_check(Path(".agent/vibe_check.md"), auto_run=True)
print(f"Passed: {result.passed}/{result.total_checks}")
```

### 4. Impact Analyzer (`impact_analyzer.py`) *(Optional)*

Uses AST parsing to detect Pydantic models and predict impact:

```python
report = analyze_impact(Path("models/user.py"), Path("."))
print(f"Risk level: {report.risk_level}")
print(f"Affects {len(report.affected_models)} models")
```

---

## 📋 Template Files

### MISSION_STATE.md
Structured document tracking project evolution:
- Current objectives
- Architecture diagram
- Development history
- Lessons learned
- Next steps

### claw_rules.md
Project-specific development constraints:
- Async-first approach
- Strong typing requirements
- Code quality standards
- Security guidelines

### vibe_check.md
Automated verification checklist:
- Unit tests
- Code coverage
- Linting
- Documentation
- Security checks

---

## 🤝 Integration Patterns

### Scenario 1: Antigravity → OpenClaw Handoff

1. Antigravity completes feature implementation
2. Antigravity updates `MISSION_STATE.md` manually
3. OpenClaw starts new session, reads `MISSION_STATE.md`
4. OpenClaw understands what was done and continues work

### Scenario 2: OpenClaw Autonomous Operation

1. OpenClaw runs `scan_repo_context()` on startup
2. Detects project rules and current mission
3. Completes task and runs `perform_vibe_check()`
4. Updates `MISSION_STATE.md` via `update_mission_log()`

### Scenario 3: Human-AI Collaboration

1. Human reviews `MISSION_STATE.md` to understand project state
2. Human adds manual notes or corrections
3. AI systems read updated state and adapt their approach
4. Continuous knowledge sharing

---

## 🧪 Testing

```bash
# Install dependencies
pip install -r requirements.txt

# Run unit tests (when implemented)
pytest tests/

# Manual testing
python -m logic.context_manager
python -m logic.mission_summarizer
python -m logic.vibe_checker
```

---

## 📝 Requirements

- Python 3.8+
- pydantic >= 2.0.0
- python-frontmatter >= 1.0.0

---

## 🗺️ Roadmap

- [ ] Add unit tests for all modules
- [ ] Implement visual dashboard for mission state
- [ ] Support for mermaid architecture diagrams
- [ ] Integration with project management tools (Jira, Linear)
- [ ] VS Code extension for quick access to mission state

---

## 🤝 Contributing

This is an experimental project exploring AI-to-AI collaboration patterns. Contributions welcome!

1. Fork the repository
2. Create a feature branch
3. Make changes with tests
4. Submit pull request

---

## 📄 License

MIT License - See LICENSE file for details

---

## 🙏 Acknowledgments

Created through collaboration between:
- **Antigravity** (Google DeepMind)
- **Human Engineer** (z8z0028z4)
- Inspired by the need for persistent AI memory and cross-system collaboration

---

## 📞 Support

- Issues: [GitHub Issues](https://github.com/z8z0028z4/GravityHook/issues)
- Discussions: [GitHub Discussions](https://github.com/z8z0028z4/GravityHook/discussions)

---

**Remember**: The goal isn't just better AI tools—it's better AI **collaboration**. 🚀
