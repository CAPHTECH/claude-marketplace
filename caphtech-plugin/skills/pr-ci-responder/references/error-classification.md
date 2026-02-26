# CI エラー分類ルール

## ログ取得手順

```bash
# 1. PRのチェック状態を確認
gh pr checks --json name,state,link

# 2. 失敗したcheckのリンクからrun_idを抽出
# link例: https://github.com/{owner}/{repo}/actions/runs/{run_id}/...
# → run_id部分を抽出

# 3. run_idが取れない場合のフォールバック
gh run list --branch $(git branch --show-current) --status failure --limit 5 --json databaseId,name,conclusion

# 4. 失敗ログを取得
gh run view {run_id} --log-failed
```

### 非GitHub Actions CI の検出

`gh pr checks` のリンクが GitHub Actions 以外を指している場合（CircleCI, Jenkins 等）:
- **即座にエスカレーション**: 自動修正は GitHub Actions のみ対応
- ユーザーに CI 環境を報告し、手動対応を依頼

## エラー分類テーブル

| カテゴリ | パターン | 優先度 | 備考 |
|----------|---------|--------|------|
| `lint` | ESLint, Prettier, Ruff, golangci-lint, dart analyze (info/warning), mix format, credo | 1（最高） | 自動修正で解消しやすい |
| `type` | TypeScript TS\d+, mypy error, Dialyzer, dart analyze (error) | 2 | 型定義の修正が必要 |
| `build` | compile error, Module not found, import error, pub get failed, mix compile | 3 | 依存関係・パス問題 |
| `test` | FAIL, AssertionError, Expected/Received, ExUnit failure, test failed | 4 | テスト or 実装の修正 |
| `other` | 上記に該当しない | 5 | 手動分析が必要 |

## 分類のガイドライン

### 優先度の根拠

低優先度のエラーは高優先度の修正で解消されることが多いため、**lint → type → build → test** の順序を厳守する。

例:
- lint修正（import順序整理）→ build エラーが解消
- type修正（型定義追加）→ test の型関連エラーが解消

### 複合エラーの扱い

1つのログ行が複数カテゴリに該当する場合、**最も高い優先度**のカテゴリに分類する。

### パターンマッチング例

```yaml
lint_patterns:
  - "ESLint"
  - "Prettier"
  - "prettier"
  - "ruff"
  - "golangci-lint"
  - "dart analyze.*info"
  - "dart analyze.*warning"
  - "mix format"
  - "credo"
  - "stylelint"

type_patterns:
  - "TS\\d{4}"     # TypeScript error codes
  - "error TS"
  - "mypy.*error"
  - "Dialyzer"
  - "dart analyze.*error"
  - "type.*mismatch"

build_patterns:
  - "compile error"
  - "compilation failed"
  - "Module not found"
  - "Cannot find module"
  - "import error"
  - "ImportError"
  - "ModuleNotFoundError"
  - "pub get failed"
  - "mix compile.*error"
  - "go build.*error"

test_patterns:
  - "FAIL"
  - "FAILED"
  - "AssertionError"
  - "AssertionError"
  - "Expected.*Received"
  - "expected.*got"
  - "ExUnit.*failure"
  - "test.*failed"
  - "pytest.*ERRORS"
  - "--- FAIL:"       # Go test

other_patterns:
  - "timeout"
  - "permission denied"
  - "rate limit"
  - "network error"
```

## 出力スキーマ

```yaml
diagnosis:
  run_id: "12345678"
  check_name: "CI / lint"
  total_errors: 5

  errors:
    - category: lint
      count: 3
      details: "ESLint: no-unused-vars (2), prettier (1)"
      files:
        - "src/api/users.ts"
        - "src/utils/helpers.ts"

    - category: test
      count: 2
      details: "FAIL src/__tests__/user.test.ts - Expected 200, got 404"
      files:
        - "src/__tests__/user.test.ts"
```
