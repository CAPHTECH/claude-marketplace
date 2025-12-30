# Phase Definitions（フェーズ定義）

各フェーズの詳細な入退場条件と成果物。

## 1. intake（Issue取り込み）

```yaml
phase:
  id: "intake"
  skill: "/issue-intake"
  purpose: "Issue初期トリアージ、分類、リスク初期評価"

  entry_criteria: []  # 最初のフェーズなので前提なし

  exit_criteria:
    - "intake_report が生成されている"
    - "classification が決定されている"
    - "severity_score が算出されている"

  on_failure: "halt_and_escalate"  # 分類できないなら人間へ

  artifacts_in: []

  artifacts_out:
    - "intake_report"
```

## 2. context（コンテキスト活性化）

```yaml
phase:
  id: "context"
  skill: "/eld-sense-activation"
  purpose: "関連知識の活性化、コード探索、再現環境構築"

  entry_criteria:
    - "intake_report が存在する"

  exit_criteria:
    - "context_pack が生成されている"
    - "risk_register が初期化されている"
    - "再現手順が確立している OR 再現不能として記録"

  on_failure: "retry"  # 情報不足なら再試行

  artifacts_in:
    - "intake_report"

  artifacts_out:
    - "context_pack"
    - "risk_register"
```

## 3. onboarding（オンボーディング）

```yaml
phase:
  id: "onboarding"
  skill: "/ai-led-onboarding"
  purpose: "最小スキーマ構築（目的・境界・不変条件・壊れ方・観測・未確定）"

  entry_criteria:
    - "context_pack が存在する"

  exit_criteria:
    - "repo_map が生成されている"
    - "6点の最小スキーマが確立している"

  on_failure: "retry"

  artifacts_in:
    - "context_pack"
    - "intake_report"

  artifacts_out:
    - "repo_map"

  skip_condition:
    - "severity == trivial"  # 軽微な修正ではスキップ可
```

## 4. uncertainty（不確実性解消）

```yaml
phase:
  id: "uncertainty"
  skill: "/resolving-uncertainty"
  purpose: "不確実性の台帳化と優先順位付け、観測タスク化"

  entry_criteria:
    - "risk_register が存在する"

  exit_criteria:
    - "unknowns が resolved OR escalated"
    - "updated_risk_register が生成されている"
    - "blocking な不確実性がない OR 人間へエスカレーション済み"

  on_failure: "pause_for_approval"  # 解消できないなら承認待ち

  artifacts_in:
    - "risk_register"
    - "context_pack"

  artifacts_out:
    - "updated_risk_register"
    - "questions_log"
```

## 5. task_decomposition（タスク分解）

```yaml
phase:
  id: "task_decomposition"
  skill: "/eld-sense-task-decomposition"
  purpose: "タスクを分解し、実装計画を策定"

  entry_criteria:
    - "context_pack が存在する"
    - "blocking な不確実性がない"

  exit_criteria:
    - "task_plan が生成されている"
    - "スコープ境界が明確"
    - "依存関係が整理されている"

  on_failure: "rollback"  # context に戻る

  artifacts_in:
    - "context_pack"
    - "updated_risk_register"

  artifacts_out:
    - "task_plan"
```

## 6. observation（観測計画）

```yaml
phase:
  id: "observation"
  skill: "/observation-minimum-set"
  purpose: "テスト計画、観測点、検証方法の策定"

  entry_criteria:
    - "task_plan が存在する"

  exit_criteria:
    - "observation_plan が生成されている"
    - "必要なテスト種別が特定されている"
    - "計測点が定義されている"

  on_failure: "retry"

  artifacts_in:
    - "task_plan"
    - "context_pack"

  artifacts_out:
    - "observation_plan"
```

## 7. implementation（実装）

```yaml
phase:
  id: "implementation"
  skill: "/eld"
  purpose: "実装ループ（Sense→Model→Predict→Change→Ground→Record）"

  entry_criteria:
    - "observation_plan が存在する"
    - "task_plan が存在する"

  exit_criteria:
    - "diff_summary が生成されている"
    - "test_report が生成されている"
    - "implementation_log が生成されている"
    - "すべての必須テストがパス"

  on_failure: "halt_and_review"  # テスト失敗なら停止

  artifacts_in:
    - "task_plan"
    - "observation_plan"
    - "context_pack"

  artifacts_out:
    - "diff_summary"
    - "test_report"
    - "implementation_log"

  stop_condition_checks:
    - "test_failure_threshold"
    - "scope_change_detected"
```

## 8. review（レビュー）

```yaml
phase:
  id: "review"
  skill: "/eld-ground-pr-review"
  purpose: "PRレビュー、証拠パック検証、マージ判断"

  entry_criteria:
    - "diff_summary が存在する"
    - "test_report が存在する"
    - "test_report.all_passed == true"

  exit_criteria:
    - "review_report が生成されている"
    - "merge_ready == true OR changes_requested"

  on_failure: "rollback"  # implementation に戻る

  artifacts_in:
    - "diff_summary"
    - "test_report"
    - "implementation_log"
    - "observation_plan"

  artifacts_out:
    - "review_report"
```

## フェーズ遷移図

```
intake → context → onboarding → uncertainty
                                     ↓
review ← implementation ← observation ← task_decomposition
```

## on_failure アクション

| action | 説明 | 遷移先 |
|--------|------|--------|
| `retry` | 同じフェーズを再試行 | 現在のフェーズ |
| `rollback` | 前のフェーズに戻る | 前フェーズ |
| `halt_and_review` | 停止してレビュー要求 | 停止状態 |
| `halt_and_escalate` | 停止して人間へエスカレーション | 停止状態 |
| `pause_for_approval` | 承認待ち | 一時停止状態 |
