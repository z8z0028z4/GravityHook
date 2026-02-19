#!/usr/bin/env bash
set -euo pipefail

ROOT="/home/clawd/foundation/gravityhook-core"
WORKDIR="${1:-/tmp/gravityhook-e2e}"
REPORT="${ROOT}/tests/artifacts/gravityhook_e2e_report.json"
LOG="${ROOT}/tests/artifacts/gravityhook_e2e.log"

rm -rf "$WORKDIR"
mkdir -p "$WORKDIR"

cat > "$WORKDIR/README.md" <<'MD'
# GravityHook E2E Sandbox

Smoke-test sandbox for GravityHook bootstrap + repo_check.
MD

"$ROOT/scripts/bootstrap_gravityhook.sh" "$WORKDIR" | tee "$LOG"

python3 "$WORKDIR/.agent/tools/repo_check.py" \
  --vibe-check "$WORKDIR/.agent/vibe_check.md" \
  --output "$REPORT" \
  --repo-path "$WORKDIR" | tee -a "$LOG"

python3 - <<PY | tee -a "$LOG"
import json
p = "$REPORT"
with open(p) as f:
    d = json.load(f)
print("== E2E Summary ==")
print(d.get("summary"))
print("agent_review_needed:", len(d.get("agent_review_needed", [])))
PY

echo "Artifacts:"
echo "- $REPORT"
echo "- $LOG"
