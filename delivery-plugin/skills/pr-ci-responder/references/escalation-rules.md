# エスカレーションルール

## エスカレーション条件

以下のいずれかに該当する場合、自動修正を中断しユーザーに委譲する。

| 条件 | 判断基準 | アクション |
|------|---------|-----------|
| 同一エラー2回連続 | 前回と同じエラーメッセージ | 中断 → エラー詳細を報告 |
| エラー数増加 | 修正前よりエラー数が増えた | ロールバック提案 → ユーザー確認 |
| CI環境固有エラー | ローカルで再現不可能 | 中断 → 環境差異を報告 |
| 最大リトライ到達 | 5回 | 中断 → 対応サマリーを報告 |
| 非GitHub Actions CI | link が Actions 以外 | 即中断 → CI環境を報告 |

## 同一エラー検出

### 判定方法

各リトライで以下を記録し、前回と比較:
- エラーカテゴリ
- エラーメッセージ（先頭100文字）
- 該当ファイル・行番号

### 同一エラーと判定する条件

以下のすべてが一致:
1. カテゴリが同じ
2. エラーメッセージの主要部分が同じ
3. 該当ファイルが同じ

## エラー数増加検出

### 判定方法

```
修正前エラー数: N
修正後エラー数: M
M > N → エスカレーション
```

### ロールバック提案

エラーが増加した場合:

```bash
# 直前のコミットを確認
git log --oneline -3

# ユーザーに確認の上でロールバック
# git revert HEAD --no-edit
```

**注意**: ロールバックはユーザー確認なしに実行しない。

## CI環境固有エラーの検出

### 判断基準

1. ローカルで同じチェックコマンドを実行して成功
2. CI ログに環境固有の情報がある:
   - Node.js / Python / Go のバージョン差異
   - OS差異（ubuntu vs macos）
   - 環境変数の欠如
   - ネットワークアクセス制限
   - Docker 関連エラー

### 報告内容

```yaml
escalation:
  reason: "ci_environment_specific"
  local_result: "PASS"
  ci_result: "FAIL"
  suspected_cause: "Node.js version mismatch (local: 20.x, CI: 18.x)"
  recommendation: "CI設定の Node.js バージョンを確認してください"
```

## 最大リトライ到達時の報告

```yaml
escalation:
  reason: "max_retries_reached"
  total_attempts: 5
  remaining_errors:
    - category: test
      count: 2
      details: "Integration test failure - API endpoint returns 500"
  recommendation: "テスト環境の設定を確認してください"
  changes_made:
    - attempt: 1
      fixes: ["lint自動修正 (3件)"]
      commit: "abc1234"
    - attempt: 2
      fixes: ["型エラー修正 (2件)"]
      commit: "def5678"
```

## エスカレーション時の出力形式

```yaml
ci_fix_result:
  pr_ref: "owner/repo#123"
  branch: "feature/xxx"
  status: "escalated"

  escalation:
    reason: "same_error_repeated" | "error_count_increased" | "ci_environment_specific" | "max_retries_reached" | "non_github_actions"
    details: "エスカレーション理由の詳細"
    recommendation: "推奨アクション"

  attempts:
    - attempt: 1
      errors_found: [...]
      fixes_applied: [...]
      commit: "abc1234"
      ci_result: "failure"

  summary:
    total_attempts: 2
    errors_fixed: 5
    errors_remaining: 2
    files_modified: [...]
    final_status: "エスカレーション: 同一エラーが2回連続"
```
