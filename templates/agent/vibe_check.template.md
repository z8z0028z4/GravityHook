# Vibe Check: Post-Development Verification

> Automated and manual verification checklist. Mark items with [x] when completed.

## Code Quality

- [!] All unit tests pass (`pytest`) <!-- FAIL: pytest not installed -->
- [!] Code coverage is at least 80% (`pytest --cov`) <!-- FAIL: pytest not installed -->
- [!] No linting errors (`ruff check`) <!-- FAIL: ruff not installed -->
- [!] Type checking passes (`mypy`) <!-- FAIL: mypy not installed -->

## Architecture Compliance

- [!] Code follows async-first principles (manual review) <!-- FAIL: All engines/ use sync I/O -->
- [~] Strong typing with Pydantic models where applicable <!-- WARNING: Uses dataclass, not Pydantic -->
- [!] No hardcoded values or magic numbers <!-- FAIL: Magic numbers found (9999, 500, 100, etc.) -->
- [!] Proper error handling (no bare except clauses) <!-- FAIL: file_mover.py:159 bare except -->

## Documentation

- [x] File exists: README.md
- [x] Public functions have docstrings <!-- PASS: 90.5% coverage -->
- [~] API changes documented in CHANGELOG.md (if applicable) <!-- N/A: No CHANGELOG.md -->
- [x] MISSION_STATE.md updated with latest changes <!-- PASS: Updated 2026-02-11 -->

## Security & Performance

- [ ] No secrets committed to repository (`git secrets --scan`)
- [ ] Environment variables used for configuration
- [ ] User inputs are sanitized
- [ ] Database queries use proper indexes (manual review)

## Integration

- [ ] Application starts without errors (`python main.py` or equivalent)
- [ ] API endpoints respond correctly (manual test or automated integration tests)
- [ ] Database migrations applied successfully (if applicable)

## Deployment Readiness

- [ ] requirements.txt or pyproject.toml updated
- [ ] Docker image builds successfully (`docker build .`)
- [ ] CI/CD pipeline passes (GitHub Actions, etc.)

---

## 🔍 Special Syntax for Automation

OpenClaw can parse this file and execute automated checks:

- **Command check**: `- [ ] Description (\`command\`)`
  - Example: `- [ ] Tests pass (\`pytest\`)`
  - OpenClaw will execute the command and mark as passed if return code is 0

- **File existence**: `- [ ] File exists: path/to/file`
  - Example: `- [ ] File exists: requirements.txt`
  - OpenClaw checks if the file exists

- **Manual check**: Any item without special syntax
  - Example: `- [ ] Code follows best practices`
  - OpenClaw will leave as pending for human verification

---

## ✅ Next Steps After Vibe Check

1. If all checks pass → Run `update_mission_log()` to record success
2. If some fail → Run `add_technical_debt()` to document issues
3. Review mission state and plan next actions
