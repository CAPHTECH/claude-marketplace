# Workflow Templates（ワークフローテンプレート）

分類に応じて選択されるワークフローテンプレート。

## trivial_fix_v1

**適用条件**: severity=trivial

**特徴**: 最小限のフェーズで迅速に完了

```yaml
template:
  id: "trivial_fix_v1"
  version: "1.0"
  phases:
    - id: "intake"
      skill: "/issue-intake"
      required: true

    - id: "implementation"
      skill: "/eld"
      required: true
      simplified: true  # 簡略化モード

    - id: "review"
      skill: "/eld-ground-pr-review"
      required: true
      simplified: true

  skipped_phases:
    - "onboarding"
    - "uncertainty"
    - "task_decomposition"
    - "observation"

  governance:
    approval_required: false
    review_depth: "light"
```

## minor_bugfix_v1

**適用条件**: severity=minor, type=bugfix

**特徴**: 標準フロー

```yaml
template:
  id: "minor_bugfix_v1"
  version: "1.0"
  phases:
    - id: "intake"
      skill: "/issue-intake"
      required: true

    - id: "context"
      skill: "/eld-sense-activation"
      required: true

    - id: "uncertainty"
      skill: "/uncertainty-resolution"
      required: false  # リスクがあれば実行

    - id: "task_decomposition"
      skill: "/eld-sense-planning"
      required: true

    - id: "observation"
      skill: "/observation-minimum-set"
      required: true

    - id: "implementation"
      skill: "/eld"
      required: true

    - id: "review"
      skill: "/eld-ground-pr-review"
      required: true

  governance:
    approval_required: false
    review_depth: "standard"
```

## major_bugfix_v2

**適用条件**: severity=major, type=bugfix

**特徴**: 標準フロー＋強化観測＋オンボーディング

```yaml
template:
  id: "major_bugfix_v2"
  version: "2.0"
  phases:
    - id: "intake"
      skill: "/issue-intake"
      required: true

    - id: "context"
      skill: "/eld-sense-activation"
      required: true

    - id: "onboarding"
      skill: "/ai-led-onboarding"
      required: true

    - id: "uncertainty"
      skill: "/uncertainty-resolution"
      required: true

    - id: "task_decomposition"
      skill: "/eld-sense-planning"
      required: true

    - id: "observation"
      skill: "/observation-minimum-set"
      required: true
      enhanced: true  # 強化モード

    - id: "implementation"
      skill: "/eld"
      required: true

    - id: "review"
      skill: "/eld-ground-pr-review"
      required: true

  governance:
    approval_required: false
    review_depth: "thorough"
    stop_conditions:
      - "scope_change_detected"
      - "test_failure_threshold"
```

## critical_hotfix_v1

**適用条件**: severity=critical

**特徴**: 緊急フロー、並列化、承認省略可

```yaml
template:
  id: "critical_hotfix_v1"
  version: "1.0"
  phases:
    - id: "intake"
      skill: "/issue-intake"
      required: true
      timeout_minutes: 5  # 短縮

    - id: "context"
      skill: "/eld-sense-activation"
      required: true
      timeout_minutes: 10

    - id: "implementation"
      skill: "/eld"
      required: true
      mode: "hotfix"  # 最小変更モード

    - id: "review"
      skill: "/eld-ground-pr-review"
      required: true
      mode: "expedited"  # 迅速モード

  skipped_phases:
    - "onboarding"
    - "uncertainty"
    - "task_decomposition"
    - "observation"  # 事後対応

  governance:
    approval_required: false  # 緊急時は省略可
    review_depth: "expedited"
    post_mortem_required: true  # 事後レビュー必須

  post_actions:
    - action: "create_follow_up_issue"
      purpose: "完全なテスト追加"
    - action: "schedule_post_mortem"
      purpose: "根本原因分析"
```

## security_fix_v1

**適用条件**: type=security

**特徴**: セキュリティ強化フロー、追加検証

```yaml
template:
  id: "security_fix_v1"
  version: "1.0"
  phases:
    - id: "intake"
      skill: "/issue-intake"
      required: true

    - id: "context"
      skill: "/eld-sense-activation"
      required: true

    - id: "security_assessment"
      skill: "/security-observation"
      required: true  # セキュリティ固有

    - id: "uncertainty"
      skill: "/uncertainty-resolution"
      required: true

    - id: "task_decomposition"
      skill: "/eld-sense-planning"
      required: true

    - id: "observation"
      skill: "/observation-minimum-set"
      required: true
      enhanced: true
      include:
        - "security_scan"
        - "dependency_audit"

    - id: "implementation"
      skill: "/eld"
      required: true

    - id: "security_review"
      skill: "/security-observation"
      required: true  # 再検証

    - id: "review"
      skill: "/eld-ground-pr-review"
      required: true

  governance:
    approval_required: true
    approver: "security_team"
    review_depth: "security"
    disclosure_policy: "coordinate"  # 脆弱性開示ポリシー
```

## feature_v1

**適用条件**: type=feature

**特徴**: 設計フェーズ追加

```yaml
template:
  id: "feature_v1"
  version: "1.0"
  phases:
    - id: "intake"
      skill: "/issue-intake"
      required: true

    - id: "context"
      skill: "/eld-sense-activation"
      required: true

    - id: "onboarding"
      skill: "/ai-led-onboarding"
      required: true

    - id: "design"
      skill: "/eld-model"
      required: true  # 設計フェーズ

    - id: "uncertainty"
      skill: "/uncertainty-resolution"
      required: true

    - id: "task_decomposition"
      skill: "/eld-sense-planning"
      required: true

    - id: "observation"
      skill: "/observation-minimum-set"
      required: true

    - id: "implementation"
      skill: "/eld"
      required: true

    - id: "review"
      skill: "/eld-ground-pr-review"
      required: true

  governance:
    approval_required: false
    review_depth: "thorough"
    design_review: true  # 設計レビューあり
```

## テンプレートバージョニング

テンプレートIDに `_v1`, `_v2` を付与することで、過去の実行と比較可能。

```yaml
versioning:
  format: "{template_name}_v{major}"
  changelog:
    major_bugfix_v2:
      changes:
        - "onboarding フェーズ追加"
        - "observation 強化モード対応"
      previous: "major_bugfix_v1"
```

## カスタムテンプレート

プロジェクト固有のテンプレートを定義可能。

```yaml
custom_template:
  id: "project_specific_v1"
  extends: "major_bugfix_v2"
  overrides:
    phases:
      - id: "custom_validation"
        skill: "/project-specific-validation"
        after: "implementation"
    governance:
      approval_required: true
      approver: "tech_lead"
```
