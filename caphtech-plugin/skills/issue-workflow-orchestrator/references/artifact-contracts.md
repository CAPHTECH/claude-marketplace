# Artifact Contracts（成果物スキーマ）

フェーズ間で引き継ぐ成果物の構造化スキーマ。

## intake_report

生成フェーズ: intake

```yaml
intake_report:
  issue_id: "#123"
  title: "認証エラーが発生する"
  type: "bug"
  classification: "Major"
  severity_score: "7/10"
  confidence: 0.72

  summary:
    symptoms: "ログイン時にエラーが発生"
    expected: "正常にログインできる"
    actual: "500エラーが返る"

  acceptance_criteria:
    - "ログインが正常に完了する"
    - "エラーログが出力されない"
    - "既存テストがパスする"

  reproduction:
    frequency: "常に"
    environment: "prod"
    steps: ["ログイン画面を開く", "認証情報を入力", "ログインボタンをクリック"]

  constraints:
    deadline: "2025-01-05"
    target_branch: "main"
    out_of_scope: ["認証方式の変更"]

  initial_risks:
    - "再現条件が完全ではない可能性"
    - "影響範囲が不明確"

  uncertainty_flags:
    - "missing_logs"
    - "missing_impact_breadth"
```

## context_pack

生成フェーズ: context

```yaml
context_pack:
  reproduction:
    minimal_steps:
      - step: 1
        action: "ログイン画面を開く"
        url: "/login"
      - step: 2
        action: "認証情報を入力"
        data: {email: "test@example.com", password: "***"}
      - step: 3
        action: "ログインボタンをクリック"
        result: "500エラー"
    environment:
      os: "macOS 14.0"
      browser: "Chrome 120"
      node_version: "20.10.0"
    reproducibility: "100%"

  logs:
    - source: "server.log"
      timestamp: "2025-12-30T10:00:00Z"
      content: "TypeError: Cannot read property 'id' of undefined"
      stack_trace: "..."

  code_scope:
    primary_files:
      - path: "src/auth/login.ts"
        lines: "45-78"
        reason: "エラー発生箇所"
      - path: "src/middleware/auth.ts"
        lines: "23-45"
        reason: "認証ミドルウェア"
    secondary_files:
      - path: "src/models/user.ts"
        reason: "Userモデル参照"

  dependencies:
    internal:
      - module: "session"
        relation: "depends_on"
      - module: "database"
        relation: "reads_from"
    external:
      - package: "jsonwebtoken"
        version: "9.0.0"

  specifications:
    - url: "docs/auth-spec.md"
      section: "ログインフロー"
```

## risk_register

生成フェーズ: context, uncertainty

```yaml
risk_register:
  unknowns:
    - id: "unknown_001"
      description: "特定のユーザーのみで発生するか不明"
      impact: "high"
      confidence: 0.3
      status: "open"  # open/investigating/resolved/escalated
      resolution_method: "ログ分析で影響ユーザーを特定"
      assigned_to: null
      deadline: null

    - id: "unknown_002"
      description: "回帰かどうか不明"
      impact: "medium"
      confidence: 0.5
      status: "resolved"
      resolution: "git bisect で v2.3.1 で導入と判明"

  escalations:
    - id: "escalation_001"
      unknown_id: "unknown_003"
      reason: "セキュリティ影響の可能性"
      escalated_to: "security_team"
      escalated_at: "2025-12-30T11:00:00Z"

  mitigations:
    - risk_id: "unknown_001"
      action: "ログレベルを DEBUG に変更して追加情報収集"
      status: "in_progress"
```

## task_plan

生成フェーズ: task_decomposition

```yaml
task_plan:
  root_task:
    id: "task_root"
    goal: "認証エラーを修正"
    success_criteria: ["ログインが成功する", "テストがパスする"]

  subtasks:
    - id: "task_1"
      goal: "エラー原因の特定"
      boundary: "src/auth/login.ts のみ"
      dependencies: []
      parallel: false
      estimated_complexity: "medium"

    - id: "task_2"
      goal: "修正実装"
      boundary: "src/auth/login.ts, src/middleware/auth.ts"
      dependencies: ["task_1"]
      parallel: false
      estimated_complexity: "medium"

    - id: "task_3"
      goal: "テスト追加"
      boundary: "src/auth/__tests__/"
      dependencies: ["task_2"]
      parallel: false
      estimated_complexity: "low"

  out_of_scope:
    - "認証方式の変更"
    - "他の認証関連バグ"
    - "パフォーマンス最適化"

  affected_files:
    - "src/auth/login.ts"
    - "src/middleware/auth.ts"
    - "src/auth/__tests__/login.test.ts"

  context_inheritance:
    - from: "root"
      to: "task_1"
      inherit: ["context_pack", "risk_register"]
      return: ["root_cause_analysis"]
```

## observation_plan

生成フェーズ: observation

```yaml
observation_plan:
  test_strategy:
    unit_tests:
      - file: "src/auth/__tests__/login.test.ts"
        cases:
          - "正常ログイン"
          - "無効な認証情報"
          - "null/undefined ユーザー"
    integration_tests:
      - file: "src/auth/__tests__/integration.test.ts"
        cases:
          - "E2E ログインフロー"
    property_tests:
      - description: "任意の有効なユーザーでログイン成功"

  measurement_points:
    - point: "auth.login.success_rate"
      type: "metric"
      threshold: ">= 99.9%"
    - point: "auth.login.latency_p99"
      type: "metric"
      threshold: "< 500ms"
    - point: "server.log"
      type: "log"
      pattern: "TypeError|undefined"
      expected: "0 matches"

  regression_checks:
    - test_suite: "auth"
      must_pass: true
    - test_suite: "smoke"
      must_pass: true

  acceptance_verification:
    - criteria: "ログインが正常に完了する"
      method: "E2E テスト"
      evidence: "test_report.e2e.login"
```

## diff_summary

生成フェーズ: implementation

```yaml
diff_summary:
  commit_sha: "abc123"
  branch: "fix/issue-123-auth-error"
  base_branch: "main"

  stats:
    files_changed: 3
    insertions: 45
    deletions: 12

  files:
    - path: "src/auth/login.ts"
      change_type: "modified"
      hunks:
        - lines: "45-52"
          description: "null チェック追加"
    - path: "src/auth/__tests__/login.test.ts"
      change_type: "modified"
      hunks:
        - lines: "78-95"
          description: "null ケースのテスト追加"

  affected_modules:
    - "auth"

  breaking_changes: false
```

## test_report

生成フェーズ: implementation

```yaml
test_report:
  summary:
    total: 45
    passed: 45
    failed: 0
    skipped: 2
    duration_seconds: 12.5

  all_passed: true

  suites:
    - name: "auth"
      passed: 20
      failed: 0
      tests:
        - name: "正常ログイン"
          status: "passed"
          duration_ms: 150
        - name: "null ユーザー処理"
          status: "passed"
          duration_ms: 80

  coverage:
    lines: 87.5
    branches: 82.3
    functions: 90.0

  new_tests:
    - "src/auth/__tests__/login.test.ts: null ユーザー処理"

  failed_details: []  # 失敗時のみ詳細
```

## review_report

生成フェーズ: review

```yaml
review_report:
  pr_number: 456
  pr_url: "https://github.com/org/repo/pull/456"

  verdict: "approved"  # approved/changes_requested/pending

  checklist:
    - item: "テストがパスしている"
      status: "passed"
    - item: "カバレッジが基準を満たす"
      status: "passed"
    - item: "静的解析がパス"
      status: "passed"
    - item: "ドキュメント更新"
      status: "not_applicable"

  evidence_pack:
    test_report: "artifact://test_report.json"
    diff_summary: "artifact://diff_summary.json"
    implementation_log: "artifact://implementation_log.json"

  merge_ready: true

  notes:
    - "null チェックの追加は適切"
    - "テストケースが網羅的"
```
