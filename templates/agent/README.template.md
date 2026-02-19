# GravityHook: AI Agent Collaboration Framework

> **Version**: 2.0 (Quality Check Pipeline Integrated)  
> **Purpose**: Enable seamless handoff and collaboration between AI agents (Cobalt, Antigravity, etc.) on software development projects.  
> **Repository**: AutoFolder-AI

---

## 🎯 What is GravityHook?

GravityHook is a **standardized project context framework** that allows AI agents to:
1. **Quickly understand** the project's current state, architecture, and goals
2. **Resume development** from where another agent left off
3. **Follow consistent** development standards and quality checks
4. **Collaborate asynchronously** across different sessions and systems

---

## 📂 Directory Structure

```
.agent/
├── README.md                    ← You are here
├── MISSION_STATE.md             ← Project facts: tasks, architecture, logs
├── vibe_check.md                ← Quality checklist (automated + manual)
├── rules/                       ← Development standards
│   ├── claw_rules.md            ← OpenClaw generic rules
│   └── project_rules.md         ← AutoFolder-AI specific rules
├── pipelines/                   ← Standardized workflows
│   └── quality_check.md         ← Quality verification pipeline
├── tools/                       ← Automation scripts
│   └── repo_check.py            ← Automated quality checker
├── skills/                      ← Agent capabilities (optional)
└── templates/                   ← Code/doc templates (optional)
```

---

## 🚀 Quick Start for Agents

### 1. Load Project Context
**Trigger**: When entering this repository or after `/new` reset.

**Steps**:
1. `cd /home/clawd/clawd/AutoFolder-AI` (or equivalent path)
2. Read `.agent/MISSION_STATE.md` → Current mission, architecture, development log
3. Read `.agent/rules/claw_rules.md` → Generic development standards
4. Read `.agent/rules/project_rules.md` → Project-specific constraints
5. Read `.agent/vibe_check.md` → Quality checklist status

**Shortcut (for Cobalt)**:
```bash
repo load AutoFolder-AI
```

---

### 2. Develop Features
Follow the standards in `.agent/rules/`, implement changes, write tests.

---

### 3. Run Quality Check
**Trigger**: After completing a feature, before marking task as "Done".

**Steps**:
1. Execute automated checks:
   ```bash
   python3 .agent/tools/repo_check.py --vibe-check .agent/vibe_check.md --output /tmp/vibe_report.json
   ```
2. Read `.agent/pipelines/quality_check.md` → Follow Step 2-4 (agent code review, report generation)
3. Update `.agent/vibe_check.md` with results
4. Decide: ✅ Pass / ⚠️ Warning / ❌ Fail (see pipeline for thresholds)

**Shortcut (for Cobalt)**:
```bash
repo check AutoFolder-AI
```

---

### 4. Record Progress
**Trigger**: When completing a milestone or wrapping up a session.

**Steps**:
1. Update `.agent/MISSION_STATE.md`:
   - Add entry to "Development Log" (date, action, context, discussion)
   - Update "Architecture Snapshot" if needed
   - Update "Next Actions"
   - Add to "Lessons & Technical Debt" if applicable
2. Commit changes

**Shortcut (for Cobalt)**:
```bash
repo sum
```

---

## 📜 Core Documents

### MISSION_STATE.md
**Purpose**: Single source of truth for project evolution.

**Contains**:
- Current Mission (objective, priority, status)
- Architecture Snapshot (tech stack, key modules)
- Development Log (chronological record of decisions)
- Lessons & Technical Debt (accumulated knowledge)
- Next Actions (prioritized TODO list)

**Update Frequency**: After every significant change.

---

### vibe_check.md
**Purpose**: Quality verification checklist.

**Contains**:
- Code Quality checks (tests, coverage, linting, typing)
- Architecture Compliance (async-first, strong typing, error handling)
- Documentation (README, docstrings, CHANGELOG)
- Security & Performance (secrets, input validation, DB indexes)
- Integration (app startup, API endpoints, migrations)
- Deployment Readiness (dependencies, Docker, CI/CD)

**Automation Syntax**:
- `` `command` `` → Automated command execution
- `File exists: path` → File existence check
- No syntax → Manual review required

**Update Frequency**: After each quality check.

---

### rules/claw_rules.md
**Purpose**: Generic OpenClaw development standards.

**Contains**:
- Async-first approach
- Strong typing requirements
- Code quality standards (max line length, docstrings)
- Testing requirements (coverage, mocking)
- Error handling principles
- Performance guidelines
- Security requirements

**Update Frequency**: Rarely (only when standards evolve).

---

### rules/project_rules.md
**Purpose**: Project-specific constraints.

**Contains**:
- Architectural integrity (UI/Engine separation for AutoFolder-AI)
- Python standards (Google-style docstrings)
- TDD requirements (test-first mentality)
- Operational guardrails (safe I/O, no silent errors)

**Update Frequency**: When project scope changes.

---

### pipelines/quality_check.md
**Purpose**: Step-by-step quality verification workflow.

**Contains**:
- Pipeline overview (input → tool → agent review → output)
- Automated tool execution instructions
- Agent code review guidelines (per category)
- Report generation format
- Decision criteria (✅/⚠️/❌)

**Update Frequency**: When quality process changes.

---

## 🛠️ Tools

### repo_check.py
**Purpose**: Automate machine-executable quality checks.

**Input**:
- `--vibe-check <path>`: Path to vibe_check.md
- `--output <path>`: JSON report output path
- `--repo-path <path>`: Repository root (default: CWD)

**Output**:
- JSON report with:
  - `automated`: Results of command/file checks
  - `agent_review_needed`: Items requiring manual review
  - `summary`: Pass/fail/pending counts

**Usage**:
```bash
python3 .agent/tools/repo_check.py \
  --vibe-check .agent/vibe_check.md \
  --output /tmp/vibe_report.json
```

---

## 🔄 Integration with Workflows

### For Cobalt (OpenClaw)
Cobalt has built-in commands that automate GravityHook usage:
- `repo load AutoFolder-AI` → Loads context (steps 1-5 above)
- `repo check AutoFolder-AI` → Runs quality pipeline
- `repo sum` → Updates MISSION_STATE.md

These are defined in `/home/clawd/clawd/protocols/COBALT_PROTOCOL.md`.

---

### For Antigravity (or other agents)
1. **Manual execution**: Follow the "Quick Start for Agents" steps above
2. **Read pipeline docs**: `.agent/pipelines/quality_check.md` is self-contained
3. **Use tools**: `repo_check.py` is language-agnostic (Python 3.8+)
4. **Parse JSON**: Tool output is in standard JSON format

---

### For Cron Jobs (Repo R&D)
Automated R&D sessions should:
1. Execute `repo load` (or manual equivalent)
2. Implement feature
3. Execute `repo check` before marking task complete
4. Update `MISSION_STATE.md` with results
5. Announce completion to designated Discord channel

---

## 📊 Quality Check Pass Criteria

### ✅ PASS
- ≥90% of all checks passed
- No critical failures (security, broken tests, build errors)
- Task can be marked as complete in MISSION_STATE.md

### ⚠️ WARNING
- 70-89% of checks passed
- Has non-blocking warnings (e.g., 87% type coverage vs. 90% target)
- Agent should decide: defer fixes or address immediately
- Log warnings in Technical Debt section

### ❌ FAIL
- <70% of checks passed
- Has critical failures (security issues, test failures, build breaks)
- **DO NOT** mark task as complete
- Add fix tasks to "Next Actions"

---

## 🔗 Related Resources

### System-Level Documentation
- **COBALT_PROTOCOL.md**: `/home/clawd/clawd/protocols/COBALT_PROTOCOL.md` → Command shortcuts
- **SUBAGENT_PROTOCOL.md**: `/home/clawd/clawd/protocols/SUBAGENT_PROTOCOL.md` → Sub-agent rules
- **RD_BACKLOG.md**: `/home/clawd/clawd/protocols/REPO_RD_BACKLOG.md` → Repo R&D tasks

### Repository Files
- **Main codebase**: `/home/clawd/clawd/AutoFolder-AI/` (engines, ui, models, tests)
- **Git repository**: Version control for all code changes

---

## 🧪 Version History

### v2.0 (2026-02-17)
- **Added**: `pipelines/quality_check.md` (standardized quality workflow)
- **Added**: `tools/repo_check.py` (automated quality checker)
- **Updated**: `vibe_check.md` (fixed automation syntax for `ruff check`)
- **Updated**: GravityHook now supports Antigravity agent collaboration

### v1.0 (2026-02-05)
- **Created**: Initial GravityHook structure
- **Added**: `MISSION_STATE.md`, `vibe_check.md`, `rules/`
- **Integrated**: Cobalt Protocol shortcuts (`repo load`, `repo sum`)

---

## 💡 Tips for Agent Developers

1. **Always load context first**: Don't assume you know the project state.
2. **Follow the pipeline**: Quality checks prevent technical debt accumulation.
3. **Document decisions**: MISSION_STATE.md is the project's memory.
4. **Respect the rules**: `.agent/rules/` define the project's design philosophy.
5. **Communicate changes**: Update MISSION_STATE.md after every milestone.

---

**For questions or improvements, consult the human developer (厚嶧) or refer to `/home/clawd/clawd/protocols/COBALT_PROTOCOL.md`.**
