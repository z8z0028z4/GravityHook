# GravityHook v2.0

Foundation-layer toolkit for repo quality governance and AI/human collaboration handoff.

> Repository: <https://github.com/z8z0028z4/GravityHook>
> 
> Current layout follows the **L0 Foundation** design (not project-specific business logic).

---

## Why this changed

This repo was upgraded from the old "single-skill utility" structure to a **foundation core** structure so it can be reused across multiple projects and agents.

Based on recent migration history:
- GravityHook is positioned as **L0 (Foundation layer)**
- R&D/System workflows consume GravityHook templates instead of coupling logic into each project
- `repo check` quality flow is standardized via template pipeline + tool

---

## What is included (v2.0)

### 1) Foundation templates (`templates/agent/`)
Reusable `.agent/` building blocks for any repo:

- `MISSION_STATE.template.md`
- `README.template.md`
- `vibe_check.template.md`
- `gravityhook.lock`
- `rules/claw_rules.md`
- `pipelines/quality_check.md`
- `tools/repo_check.py`

### 2) Bootstrap script (`scripts/bootstrap_gravityhook.sh`)
Script to initialize/adopt GravityHook structure in target repositories.

### 3) Collaboration spec (`specs/collaboration.md`)
Defines collaboration expectations and handoff model.

### 4) Test fixtures (`tests/`)
- `setup_test_env.sh`
- `artifacts/gravityhook_e2e.log`
- `artifacts/gravityhook_e2e_report.json`

---

## Repository structure

```text
GravityHook/
├── VERSION
├── README.md
├── requirements.txt
├── scripts/
│   └── bootstrap_gravityhook.sh
├── specs/
│   └── collaboration.md
├── templates/
│   └── agent/
│       ├── MISSION_STATE.template.md
│       ├── README.template.md
│       ├── vibe_check.template.md
│       ├── gravityhook.lock
│       ├── rules/claw_rules.md
│       ├── pipelines/quality_check.md
│       └── tools/repo_check.py
└── tests/
    ├── setup_test_env.sh
    └── artifacts/
```

---

## Usage

### A) Run quality checker template tool

`repo_check.py` is designed to run inside a target repo that has `.agent/vibe_check.md`.

```bash
python3 templates/agent/tools/repo_check.py \
  --vibe-check /path/to/repo/.agent/vibe_check.md \
  --repo-path /path/to/repo \
  --output /tmp/vibe_report.json
```

### B) Bootstrap a target repo (recommended)

```bash
bash scripts/bootstrap_gravityhook.sh /path/to/target-repo
```

Then review generated `.agent/` files and adjust rules/checklist to project needs.

---

## Compatibility notes

- Runtime target: Python 3.8+
- `repo_check.py` currently uses Python standard library only
- Existing projects can adopt this incrementally by copying `.agent/` templates

---

## Quick daily usage examples

### 1) New repo bootstrap (day 0)
Use GravityHook to initialize a project with shared `.agent/` standards.

```bash
bash scripts/bootstrap_gravityhook.sh /path/to/target-repo
```

Then confirm these files exist in target repo:
- `.agent/MISSION_STATE.md`
- `.agent/vibe_check.md`
- `.agent/rules/claw_rules.md`
- `.agent/pipelines/quality_check.md`

### 2) Before marking a task done (quality gate)
Run the checklist tool against project `.agent/vibe_check.md`.

```bash
python3 templates/agent/tools/repo_check.py \
  --vibe-check /path/to/repo/.agent/vibe_check.md \
  --repo-path /path/to/repo \
  --output /tmp/vibe_report.json
```

Use `/tmp/vibe_report.json` as review evidence before closing task/PR.

### 3) Cross-agent handoff (Cobalt ↔ Antigravity)
When one agent finishes implementation:
- Update `.agent/MISSION_STATE.md` with summary + next actions
- Keep `.agent/rules/` and `.agent/pipelines/` unchanged unless intentionally revised
- Next agent starts by reading:
  1. `.agent/MISSION_STATE.md`
  2. `.agent/rules/claw_rules.md`
  3. `.agent/pipelines/quality_check.md`

This keeps context durable across sessions and tools.

---

## Roadmap (next)

- Stabilize bootstrap CLI options and non-interactive mode
- Add CI workflow for template integrity checks
- Add regression test cases for checklist parsing edge-cases
- Publish migration guide from legacy GravityHook layout

---

## Maintainer notes

This README reflects the current Foundation migration state (v2.0 core).
If you still need the old legacy skill layout, preserve it in a separate branch/tag before further changes.
