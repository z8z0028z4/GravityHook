# Skill Index

> **Purpose**: This file lists all available skills in the project. AI assistants should check this file to determine which skills are available and when to use them.

---

## 📦 Available Skills

| Skill Name | Description | Trigger Condition | Path |
|:---|:---|:---|:---|
| **GravityHook Core** | Session management, mission state, vibe checks | Session start, task completion | `SKILL_MANIFEST.md` |

---

## 🔍 How to Use This Index

1. **At Session Start**: Scan this list to know what capabilities are available
2. **When Matching Conditions**: If a user request matches a trigger condition, read the corresponding skill before proceeding
3. **When Uncertain**: If a task seems specialized, check if a relevant skill exists

---

## ➕ Adding New Skills

When a new skill is added to `.agent/skills/`, update this index:

```markdown
| Skill Name | Description | Trigger Condition | Path |
|:---|:---|:---|:---|
| New Skill | What it does | When to use it | `.agent/skills/skill-name/SKILL.md` |
```

---

## 📋 Skill Detection Rules

AI assistants should apply skills when:

1. **Explicit Request**: User mentions the skill by name
2. **Contextual Match**: Task clearly falls within the skill's domain
3. **Complexity Threshold**: Task requires specialized knowledge beyond general coding

**Default Behavior**: If no skill matches, proceed with standard coding practices defined in `claw_rules.md`.
