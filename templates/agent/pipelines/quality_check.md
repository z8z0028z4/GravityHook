# Quality Check Pipeline

> **Purpose**: Standardized quality verification process for repository development.  
> **Target Users**: Cobalt, Antigravity, or any AI agent working on this repo.  
> **Trigger**: After completing a development task, before updating MISSION_STATE.md as "Done".

---

## 📋 Pipeline Overview

```
Input: Repo path + vibe_check.md path
  ↓
Step 1: Automated Tool Execution (repo_check.py)
  ↓
Step 2: Agent Code Review (manual items)
  ↓
Step 3: Generate Report & Update vibe_check.md
  ↓
Output: Quality status (✅ Pass / ⚠️ Warning / ❌ Fail)
```

---

## 🔧 Step 1: Automated Tool Execution

**Objective**: Run all machine-executable checks.

### 1.1 Execution Command
```bash
cd /home/clawd/clawd/AutoFolder-AI
python .agent/tools/repo_check.py --vibe-check .agent/vibe_check.md --output /tmp/vibe_report.json
```

### 1.2 Expected Output
The tool will generate `/tmp/vibe_report.json`:
```json
{
  "timestamp": "2026-02-17T09:44:00Z",
  "repo_path": "/home/clawd/clawd/AutoFolder-AI",
  "automated": [
    {"item": "pytest", "status": "pass", "command": "pytest", "output": "..."},
    {"item": "ruff check", "status": "fail", "command": "ruff check .", "output": "..."}
  ],
  "agent_review_needed": [
    {"item": "Code follows async-first principles", "files_to_check": ["engines/*.py"]},
    {"item": "MISSION_STATE.md updated", "last_modified": "2026-02-15T12:00:00Z"}
  ],
  "summary": {
    "total_items": 20,
    "automated": 8,
    "passed": 6,
    "failed": 2,
    "pending": 10
  }
}
```

### 1.3 Error Handling
- If `repo_check.py` not found → Skip Step 1, proceed to Step 2 (agent does all checks manually)
- If tool crashes → Log error, proceed to Step 2

---

## 🧠 Step 2: Agent Code Review

**Objective**: Review items that require human-like understanding.

### 2.1 Read Analysis Targets
From `/tmp/vibe_report.json`, extract the `agent_review_needed` array.

### 2.2 Review Process (for each item)

#### A. Architecture Compliance
**Check**: "Code follows async-first principles"
1. Read `.agent/rules/claw_rules.md` → locate "Async-First Approach" section
2. Scan files in `engines/` directory
3. Verify: All I/O operations use `async/await`
4. **Pass**: If ≥95% of I/O functions are async  
   **Fail**: If synchronous `open()`, `requests.get()`, etc. detected

**Check**: "Strong typing with Pydantic models"
1. Read `.agent/rules/claw_rules.md` → locate "Strong Typing" section
2. Scan `models.py` and function signatures
3. Verify: Type hints present, Pydantic models used for data validation
4. **Pass**: If ≥90% of functions have type hints  
   **Fail**: If `Any` type used excessively or missing type hints

**Check**: "No hardcoded values or magic numbers"
1. Scan all `.py` files for bare numbers/strings (exclude: 0, 1, True, False, "")
2. Verify: Constants defined at module top or in config files
3. **Pass**: If all magic values are named constants  
   **Fail**: If unexplained literals found (e.g., `if x > 42:`)

**Check**: "Proper error handling"
1. Search for `except:` patterns (bare except clauses)
2. Verify: All exceptions are typed, errors are logged
3. **Pass**: No bare `except:` found  
   **Fail**: If bare except or suppressed errors detected

#### B. Documentation
**Check**: "Public functions have docstrings"
1. Parse all `.py` files, extract public function definitions (not starting with `_`)
2. Count: Total public functions vs. those with docstrings
3. **Pass**: ≥80% have docstrings  
   **Fail**: <80%

**Check**: "MISSION_STATE.md updated with latest changes"
1. Read `MISSION_STATE.md` → extract last entry in "Development Log"
2. Run `git log -1 --oneline` to get latest commit message
3. Compare: Does the MISSION_STATE log entry mention the same changes?
4. **Pass**: If last log entry is dated ≤24h from last commit  
   **Fail**: If MISSION_STATE is stale (>48h gap)

#### C. Security
**Check**: "User inputs are sanitized"
1. Read `.agent/rules/project_rules.md` → locate "Security Requirements"
2. Search for input handling code (e.g., `input()`, API endpoints, file paths from user)
3. Verify: Validation/sanitization present (regex, type checking, path normalization)
4. **Pass**: All user inputs validated  
   **Fail**: If raw user input used directly

### 2.3 Record Results
Create a mental or temporary log:
```
Agent Review Results:
- Async-first principles: ✅ PASS (95% async coverage)
- Strong typing: ⚠️ WARNING (87% coverage, acceptable)
- No hardcoded values: ❌ FAIL (Found magic number 42 in main.py:123)
- Error handling: ✅ PASS
- Docstrings: ✅ PASS (82%)
- MISSION_STATE updated: ✅ PASS (last entry 2h ago)
- Input sanitization: ✅ PASS
```

---

## 📊 Step 3: Generate Report & Update vibe_check.md

### 3.1 Merge Results
Combine automated results (from Step 1) + agent review results (from Step 2).

### 3.2 Update vibe_check.md
- For each item in `vibe_check.md`:
  - If **PASS**: `- [ ]` → `- [x]`
  - If **FAIL**: `- [ ]` → `- [!]` (add inline note: `<!-- FAIL: reason -->`)
  - If **WARNING**: `- [ ]` → `- [~]` (add inline note: `<!-- WARNING: reason -->`)

Example:
```markdown
## Code Quality
- [x] All unit tests pass (`pytest`)
- [!] Code coverage is at least 80% (`pytest --cov`) <!-- FAIL: Only 65% coverage -->
- [x] No linting errors (`ruff check`)
- [~] Type checking passes (`mypy`) <!-- WARNING: 3 minor issues, non-blocking -->
```

### 3.3 Generate Summary Report
Format:
```
🔍 Quality Check Report
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📅 Date: 2026-02-17 09:44 UTC
📂 Repo: AutoFolder-AI

✅ PASSED (12/20)
• All unit tests pass
• No linting errors
• Async-first principles
• ...

⚠️ WARNINGS (3/20)
• Type checking: 3 minor issues
• Code coverage: 65% (target 80%)
• ...

❌ FAILED (2/20)
• Hardcoded values detected: main.py:123
• CHANGELOG.md not updated

📝 Next Actions:
1. Fix hardcoded value in main.py
2. Update CHANGELOG.md
3. Improve test coverage to 80%

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Overall Status: ⚠️ NEEDS IMPROVEMENT
(Pass threshold: ≥90% items passed)
```

### 3.4 Determine Overall Status
- **✅ PASS**: ≥90% items passed, no critical failures
- **⚠️ WARNING**: 70-89% passed, or has non-blocking warnings
- **❌ FAIL**: <70% passed, or has critical failures (security, broken tests)

---

## 🎯 Step 4: Decision & Action

### If Status = ✅ PASS
1. Update `MISSION_STATE.md` → mark current task as complete
2. Commit changes: `git add . && git commit -m "feat: [task name] (quality check passed)"`
3. Proceed to next task

### If Status = ⚠️ WARNING
1. Log warnings in `MISSION_STATE.md` → Technical Debt section
2. **Agent decision**:
   - If warnings are acceptable (e.g., 87% type coverage is close to 90%) → Proceed
   - If warnings should be fixed → Add to "Next Actions" in MISSION_STATE.md
3. Commit with note: `git commit -m "feat: [task] (⚠️ with warnings, see Technical Debt)"`

### If Status = ❌ FAIL
1. **DO NOT** mark task as complete in MISSION_STATE.md
2. Log failures in `MISSION_STATE.md` → Technical Debt section
3. Add fix tasks to "Next Actions"
4. **Agent decision**:
   - If this is a Cron job → Report failure, schedule retry
   - If interactive → Ask human: "Quality check failed. Fix now or defer?"

---

## 🔄 Integration with Workflows

### For Cobalt (via `repo check` command)
```bash
# User triggers:
repo check AutoFolder-AI

# Cobalt executes:
1. cd /home/clawd/clawd/AutoFolder-AI
2. Read .agent/pipelines/quality_check.md
3. Execute Step 1-4
4. Report summary to Discord channel
```

### For Antigravity (manual execution)
```bash
# Antigravity reads:
.agent/pipelines/quality_check.md

# Executes Step 1:
python .agent/tools/repo_check.py --vibe-check .agent/vibe_check.md --output /tmp/vibe_report.json

# Executes Step 2-4:
(Follows the documented review process)
```

### For Repo RD Cron
```yaml
# In Repo RD Cron job message:
"你是 Cobalt。請執行 Repo R&D 任務：
1. 讀取 REPO_RD_BACKLOG.md，選擇 Priority 任務
2. repo load {project_name}
3. 實作功能
4. **執行 repo check {project_name}** ← 觸發此 Pipeline
5. 若通過，更新 MISSION_STATE.md 並 repo sum
6. 推播結果至 Discord"
```

---

## 🛠️ Tool Specification

### repo_check.py Requirements

**Input**:
- `--vibe-check <path>`: Path to vibe_check.md
- `--output <path>`: Path to JSON output file (default: /tmp/vibe_report.json)

**Output**: JSON file with structure:
```json
{
  "timestamp": "ISO8601",
  "repo_path": "string",
  "automated": [{"item": "string", "status": "pass|fail|skip", "command": "string", "output": "string"}],
  "agent_review_needed": [{"item": "string", "files_to_check": ["string"], "context": "string"}],
  "summary": {"total_items": int, "automated": int, "passed": int, "failed": int, "pending": int}
}
```

**Behavior**:
1. Parse vibe_check.md
2. Identify automated items (those with `` `command` `` or `File exists:`)
3. Execute commands, record results
4. Identify manual items (those without automation syntax)
5. Write JSON report
6. Exit with code 0 (even if checks fail; report contains status)

---

## 📌 Notes for Agent Developers

### When to Use This Pipeline
- **After** implementing a feature
- **Before** marking task as complete in MISSION_STATE.md
- **Before** committing code
- **Optionally** during development (iterative checks)

### Flexibility
- Agents can adjust pass/fail thresholds based on context
- Non-blocking warnings can be deferred if justified
- Critical failures (security, broken builds) should always block

### Logging
- All pipeline executions should log to: `.agent/logs/quality_check_YYYY-MM-DD_HH-MM.log`
- Include: timestamp, status, full report, agent decisions

---

## 🔗 Related Documents
- **vibe_check.md**: The checklist being validated
- **rules/claw_rules.md**: Development standards for this repo
- **rules/project_rules.md**: Project-specific rules
- **MISSION_STATE.md**: Where to record results and technical debt
