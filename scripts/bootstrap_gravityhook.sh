#!/bin/bash
# GravityHook Bootstrap Script
# 用途：為新專案初始化 .agent/ 目錄

set -euo pipefail

REPO_PATH="${1:-.}"
TEMPLATE_PATH="/home/clawd/foundation/gravityhook-core/templates/agent"

if [ -d "$REPO_PATH/.agent" ]; then
  echo "✅ .agent/ already exists at $REPO_PATH"
  exit 0
fi

echo "🔧 Initializing .agent/ from GravityHook template..."
cp -r "$TEMPLATE_PATH" "$REPO_PATH/.agent"

# 移除 .template 後綴
mv "$REPO_PATH/.agent/vibe_check.template.md" "$REPO_PATH/.agent/vibe_check.md" 2>/dev/null || true
mv "$REPO_PATH/.agent/MISSION_STATE.template.md" "$REPO_PATH/.agent/MISSION_STATE.md" 2>/dev/null || true
mv "$REPO_PATH/.agent/README.template.md" "$REPO_PATH/.agent/README.md" 2>/dev/null || true

# 建立 gravityhook.lock
cat > "$REPO_PATH/.agent/gravityhook.lock" <<EOF
gravityhook_version: 2.0.0
profile: repo
repo_check_version: 1.0.0
quality_pipeline: default
initialized_at: $(date -u +%Y-%m-%dT%H:%M:%SZ)
EOF

echo "✅ GravityHook initialized at $REPO_PATH/.agent/"
echo "📝 Don't forget to customize MISSION_STATE.md and project_rules.md"
