# GravityHook Collaboration Contract

## Purpose
定義 AI agents 如何協作開發專案的標準流程與品質門檻。

## Principles
1. 所有開發專案必須有 .agent/ 目錄
2. 品質檢查是強制的（不可跳過）
3. 失敗時記錄 Technical Debt，不標記完成
4. 規範固化於 rules/，不因 agent 切換而改變

## Core Components
- **MISSION_STATE.md**: 專案任務、架構快照、開發日誌、技術債
- **vibe_check.md**: 品質檢查清單（自動化 + 人工審查）
- **rules/**: 開發規範（claw_rules.md + project_rules.md）
- **pipelines/**: 標準化工作流（quality_check.md）
- **tools/**: 自動化工具（repo_check.py）

## Quality Standards
- ✅ PASS: ≥90% 檢查項目通過，無 critical failures
- ⚠️ WARNING: 70-89% 通過，或有 non-blocking warnings
- ❌ FAIL: <70% 通過，或有 critical failures

詳細內容參考：`/home/clawd/clawd/protocols/GRAVITYHOOK_V2_SPEC.md`
