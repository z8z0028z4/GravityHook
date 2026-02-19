# Mission State: AutoFolder-AI 🗂️

> Fact source for project evolution and AI-to-AI handoff.

## 🎯 Current Mission
**"AI-Driven Cold Start & Rule Recommendation"**
- **Objective**: Implement a feature that scans unmanaged folders and suggests organization rules using AI.
- **Priority**: High
- **Status**: Planning & Design

---

## 🏗️ Architecture Snapshot
- **Language**: Python 3.10+
- **UI Framework**: PySide6 (Layered Architecture)
- **Core Engine**: Async-first folder scanning and simulation.
- **Key Modules**: 
  - `engines/folder_scanner.py`: Local scanning logic.
  - `engines/simulation_engine.py`: Previewing rule impacts.
  - `ui/rule_editor.py`: Manual rule management.

---

## 📜 Development Log

### [2026-02-11] Technical Prototype Verification (Subagent)
- **Action**: Created and executed `mock_test.py` to simulate AI classification logic.
- **Context**: Verified the workflow for generating automation rules from file scans.
- **Discussion**: The mock engine successfully categorized files into Images, Documents, and Videos with confidence scoring.

### [2026-02-07] Shift to Classification Quality Evaluation
- **Action**: Refocused the roadmap from direct recommendation to "Quality Evaluation" first.
- **Context**: Established that AI recommendations need a benchmark of "what constitutes good organization."
- **Discussion**: Defined initial metrics for the upcoming `engines/structure_analyzer.py`: Entropy/Clutter Index, Fragmentation, Naming Consistency, and Hierarchy Balance.

### [2026-02-05] Mission Initialization
- **Action**: Initialized GravityHook in the repository.
- **Context**: Established connection between OpenClaw and project rules.
- **Discussion**: Defined the roadmap for the AI Rule Recommender.

---

## 💡 Lessons & Technical Debt

### Lessons Learned
- **Lesson**: Project requires strict `async` handling for UI responsiveness during deep scans.
- **Lesson**: Need to ensure the AI recommender doesn't trigger massive Token usage for large directories.

### Technical Debt (2026-02-17 Quality Check)
**Status**: ❌ Quality check FAILED (19% pass rate)

**Critical Issues** (Must Fix):
- [ ] **Async-first violation**: All `engines/*.py` use synchronous I/O (violates claw_rules.md)
  - Affected: `folder_scanner.py`, `metadata_manager.py`, `operation_history.py`
  - Required: Refactor to `async def` + `aiofiles`
- [ ] **Magic numbers**: Hardcoded values without named constants
  - `file_mover.py:99` (9999), `watchman.py` (500, 100, 0.5, 1.0), `main_window.py:833` (10)
  - Required: Define constants at module top or in `constants.py`
- [ ] **Bare except clause**: `file_mover.py:159` suppresses all exceptions
  - Required: Change to `except Exception as e:` + logging

**Environment Setup** (Non-Blocking):
- [ ] Install dev tools: `pytest`, `pytest-cov`, `ruff`, `mypy`
- [ ] Run automated tests and linting

**Quality Improvement** (Optional):
- [ ] Consider migrating from `dataclass` to Pydantic models (stronger validation)
- [ ] Add CHANGELOG.md for version tracking
- [ ] Set up CI/CD pipeline

**Log**: `.agent/logs/quality_check_2026-02-17_10-35.log`

---

## ⏭️ Next Actions
1. [ ] Implement `engines/structure_analyzer.py` to calculate folder health metrics.
2. [ ] Develop "Scan & Stat" logic to quantify rule coverage and unmanaged file ratios.
3. [ ] Design AI prompt strategy for scoring classification quality (0-100).
4. [ ] Prototype a "Folder Health Dashboard" UI.
